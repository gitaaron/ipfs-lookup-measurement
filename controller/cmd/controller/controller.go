package main

import (
	"encoding/base64"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"sync"
	"time"

	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/config"
	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/server"
	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/simplenode"
)

func main() {
	simpleNodesFile := flag.String("l", "nodes-list.out", "nodes list file")
	intervalSeconds := flag.Int("i", 0, "interval between each test")

	flag.Parse()
	nodesList, err := config.GetNodesList(*simpleNodesFile)

	if err != nil {
		panic(err)
	}

	// Try to load key
	keyStr, err := ioutil.ReadFile(".key")
	if err != nil {
		fmt.Printf("error in getting the key: %v\n", err.Error())
		return
	}
	key, err := base64.StdEncoding.DecodeString(string(keyStr))
	if err != nil {
		fmt.Printf("error decoding key string: %v\n", err.Error())
		return
	}
	if len(key) != 32 {
		fmt.Printf("Wrong key size, expect 32, got: %v\n", len(key))
		return
	}

	// At start up, ask for list of node IDs.
	// If node ID is not provided then it is probably because IPFS
	// up yet so wait and try again until all are given
	ids := make([]string, 0)
	var wg sync.WaitGroup

	for _, node := range nodesList {
		fmt.Printf("Start asking for node id from %v\n", node)
		wg.Add(1)

		go func(wg *sync.WaitGroup, node config.AgentNode) {
			defer wg.Done()
			for i := 0; i < 20; i++ {

				if i == 19 {
					panic(errors.New("Timing out on IPFS ID retrieval."))
				}

				id, err := server.RequestGetID(node.Host(), key)

				if err != nil {
					fmt.Printf("error getting node id for %v: %v\n", node, err.Error())
					time.Sleep(1 * time.Second)
					continue
				}

				if len(id) > 0 {
					fmt.Printf("Got node id for %v: %v\n", node, id)
					ids = append(ids, id)
					break
				}

			}
		}(&wg, node)

	}
	wg.Wait()
	// Ask every node to set IDs.
	for _, node := range nodesList {
		fmt.Printf("Start asking node %v to set up ids\n", node)
		out, err := server.RequestSetID(node.Host(), key, ids)
		if err != nil {
			fmt.Printf("error setting id for node %v: %v", node, err.Error())
			return
		}
		fmt.Printf("Got response for setting id for node %v: %v\n", node, out)
	}

	// Initialize some file sizes at different orders of magnitude
	// 0.05 MB
	EXTRA_SMALL_SIZE := int(math.Round(0.05 * 1024 * 1024))
	// ~0.5 MB
	SMALL_SIZE := EXTRA_SMALL_SIZE * 10
	// ~5 MB
	MED_SIZE := SMALL_SIZE * 10
	// ~50 MB
	LARGE_SIZE := MED_SIZE * 10

	// Initialize vars for delayed run tracking
	var mainDelayedPlayer int = 0
	var LAST_PLAYER int = len(nodesList) - 1
	var delayedCid string
	delayedInProgress := false
	currentDelayedRun := 0
	currentDelayedSkip := 0
	const MAX_SKIPS int = 30
	var DELAYED_FILE_SIZE int = EXTRA_SMALL_SIZE

	// Start the experiment.
	for {
		performedFirstPart := false
		performedSecondPart := false

		e := simplenode.NewExperiment()

		performExtraSmallOnlyRun := func() {

			for mainPlayer := 0; mainPlayer < len(nodesList); mainPlayer++ {

				log.Println("start mainPlayer retriever run file_size: ", EXTRA_SMALL_SIZE)
				e.DoRun(key, mainPlayer, simplenode.Retriever, nodesList, EXTRA_SMALL_SIZE)

				log.Println("start mainPlayer publisher run file_size: ", EXTRA_SMALL_SIZE)
				e.DoRun(key, mainPlayer, simplenode.Publisher, nodesList, EXTRA_SMALL_SIZE)

				log.Println("one retrieval and publish run is done for node: ", mainPlayer)

			}

		}

		performOtherSizesRun := func() {

			for mainPlayer := 0; mainPlayer < len(nodesList); mainPlayer++ {

				log.Println("start mainPlayer retriever run file_size: ", SMALL_SIZE)
				e.DoRun(key, mainPlayer, simplenode.Retriever, nodesList, SMALL_SIZE)

				log.Println("start mainPlayer retriever run file_size: ", MED_SIZE)
				e.DoRun(key, mainPlayer, simplenode.Retriever, nodesList, MED_SIZE)

				log.Println("start mainPlayer retriever run file_size: ", LARGE_SIZE)
				e.DoRun(key, mainPlayer, simplenode.Retriever, nodesList, LARGE_SIZE)

				log.Println("start mainPlayer publisher run file_size: ", SMALL_SIZE)
				e.DoRun(key, mainPlayer, simplenode.Publisher, nodesList, SMALL_SIZE)

				log.Println("start mainPlayer publisher run file_size: ", MED_SIZE)
				e.DoRun(key, mainPlayer, simplenode.Publisher, nodesList, MED_SIZE)

				log.Println("start mainPlayer publisher run file_size: ", LARGE_SIZE)
				e.DoRun(key, mainPlayer, simplenode.Publisher, nodesList, LARGE_SIZE)

				log.Println("one retrieval and publish experiment is done for node:", mainPlayer)

			}

		}

		performFirstPartOfDelayed := func() (string, error) {
			log.Println("start delayed first part of run file_size: ", EXTRA_SMALL_SIZE)
			return e.DoFirstPartOfRun(key, mainDelayedPlayer, simplenode.Publisher, nodesList, DELAYED_FILE_SIZE)
		}

		performSecondPartOfDelayed := func(currentCid string) {
			log.Println("start delayed second part of cid: ", currentCid)
			e.DoSecondPartOfRun(currentCid, key, mainDelayedPlayer, simplenode.Publisher, nodesList, DELAYED_FILE_SIZE)
			log.Printf("first part of delayed run is done for cid:%s node:%d \n", currentCid, mainDelayedPlayer)
		}

		shouldPerformFirstDelayedPart := func() bool {
			return delayedInProgress == false && currentDelayedRun == 0
		}

		shouldPerformSecondDelayedPart := func() bool {
			return delayedInProgress == true && currentDelayedRun == currentDelayedSkip
		}

		if shouldPerformFirstDelayedPart() {
			delayedInProgress = true
			delayedCid, err = performFirstPartOfDelayed()
			performedFirstPart = true
			if err != nil {
				log.Println("Error performing first part: ", err)
				delayedInProgress = false
				delayedCid = ""
			} else {
				log.Printf("first part of delayed run is done for cid:%s node:%d \n", delayedCid, mainDelayedPlayer)
			}

		}

		if shouldPerformSecondDelayedPart() {
			performSecondPartOfDelayed(delayedCid)
			delayedInProgress = false
			performedSecondPart = true
			delayedCid = ""
		}

		for i := 0; i < 6; i++ {
			performExtraSmallOnlyRun()
		}

		performOtherSizesRun()

		log.Println("one round of experiments is done")
		log.Printf("performedFirstPart:%t performedSecondPart:%t currentDelayedRun:%d, currentDelayedSkip:%d delayedInProgress:%t mainDelayedPlayer:%d delayedCid:%s\n",
			performedFirstPart, performedSecondPart, currentDelayedRun, currentDelayedSkip, delayedInProgress, mainDelayedPlayer, delayedCid)

		if *intervalSeconds == 0 {
			break
		}

		currentDelayedRun++
		if performedSecondPart {
			currentDelayedRun = 0
			currentDelayedSkip += 5
			if currentDelayedSkip > MAX_SKIPS {
				currentDelayedSkip = 0
			}
			mainDelayedPlayer++
			if mainDelayedPlayer > LAST_PLAYER {
				mainDelayedPlayer = 0
			}
		}

		time.Sleep(time.Duration(*intervalSeconds) * time.Second)
	}
}
