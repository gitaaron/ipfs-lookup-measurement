package main

import (
	"encoding/base64"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"os"
	"os/exec"
	"sync"
	"time"

	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/config"
	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/server"
	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/simplenode"
)

func getRestartCLI() string {
	wd, err := os.Getwd()
	if err != nil {
		panic(err)
	}
	return fmt.Sprintf("%s/restart_agents.sh", wd)
}

func parseCmdLine() (string, int){
		simpleNodesFile := flag.String("l", "nodes-list.out", "nodes list file")
		intervalSeconds := flag.Int("i", 0, "interval between each test")
		flag.Parse()
		return *simpleNodesFile, *intervalSeconds
}

func getNodes(simpleNodesFile string) ([]config.AgentNode, []byte, *simplenode.RunState, error) {
	nodesList, err := config.GetNodesList(simpleNodesFile)

	if err != nil {
		return nil, nil, nil, err
	}

	// Try to load key
	keyStr, err := ioutil.ReadFile(".key")
	if err != nil {
		fmt.Printf("error in getting the key: %v\n", err.Error())
		return nil, nil, nil, err
	}
	key, err := base64.StdEncoding.DecodeString(string(keyStr))
	if err != nil {
		fmt.Printf("error decoding key string: %v\n", err.Error())
		return nil, nil, nil, err
	}
	if len(key) != 32 {
		fmt.Printf("Wrong key size, expect 32, got: %v\n", len(key))
		return nil, nil, nil, err
	}

	return nodesList, key, new(simplenode.RunState), nil

}

func getSetIDS(nodesList []config.AgentNode, key []byte) error {
	// Ask for list of node IDs.
	// If node ID is not provided then it is probably because IPFS
	// up yet so wait and try again until all are given
	ids := make([]string, 0)
	var wg sync.WaitGroup

	for _, node := range nodesList {
		fmt.Printf("Start asking for node id from %v\n", node)
		wg.Add(1)

		go func(wg *sync.WaitGroup, node config.AgentNode) {
			defer wg.Done()
			for i := 0; i < 240; i++ {

				if i == 239 { // giving up after 10 min.
					panic(errors.New("timing out on IPFS ID retrieval"))
				}

				id, err := server.RequestGetID(node.Host(), key)

				if err != nil {
					fmt.Printf("error getting node id for %v: %v\n", node, err.Error())
					time.Sleep(5 * time.Second)
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
			return err
		}
		fmt.Printf("Got response for setting id for node %v: %v\n", node, out)
	}
	return nil
}

func main() {

	simpleNodesFile, intervalSeconds := parseCmdLine()

	// Initialize some file sizes at different orders of magnitude
	// 0.05 MB
	EXTRA_SMALL_SIZE := int(math.Round(0.05 * 1024 * 1024))
	// ~0.5 MB
	SMALL_SIZE := EXTRA_SMALL_SIZE * 10
	// ~5 MB
	MED_SIZE := SMALL_SIZE * 10
	// ~50 MB
	LARGE_SIZE := MED_SIZE * 10

	var numExperimentsPerformed = 1

	var DELAYED_FILE_SIZE int = EXTRA_SMALL_SIZE + 10 // adding 10 so that delayed runs can be tracked by file size

	// Start the experiment.
	for {

		// first check for stop and restart signals
		if _, err := os.Stat("./stop_experiment.cmd"); err == nil {
			log.Println("called stop experiment...")
			err := os.Remove("./stop_experiment.cmd")
			if err != nil {
				panic(err)
			}
			break
		}

		if _, err := os.Stat("./restart_agents.cmd"); err == nil {
			log.Println("called restart agents...")
			out, err := exec.Command("sh", getRestartCLI()).CombinedOutput()
			if err != nil {
				log.Printf("Error while trying to restart agents:%s err:%v\n", out, err)
				panic(err)
			}
			log.Printf("restart out:%s\n", out)

			rm_err := os.Remove("./restart_agents.cmd")
			if rm_err != nil {
				panic(err)
			}
		}

		nodesList, key, runState, err := getNodes(simpleNodesFile)

		if err != nil {
			panic(err)
		}

		// get and set agent IDS on each run so that analysis has log of agent's PeerId
		getSetIDS(nodesList, key)

		e := simplenode.NewExperiment()

		performDelayedRun := func() {
			log.Println("Start performing delayed runs...")
			for mainPlayer := 0; mainPlayer < len(nodesList); mainPlayer++ {
				runState.Wg.Add(3)
				log.Println("queue delayed run with 0 sec. delay")
				go e.DoRun(runState, key, mainPlayer, simplenode.Publisher, nodesList, DELAYED_FILE_SIZE, 0)
				log.Println("queue delayed run with 60 sec. delay")
				go e.DoRun(runState, key, mainPlayer, simplenode.Publisher, nodesList, DELAYED_FILE_SIZE, 60)
				log.Println("queue delayed run with 120 sec. delay")
				go e.DoRun(runState, key, mainPlayer, simplenode.Publisher, nodesList, DELAYED_FILE_SIZE, 120)
			}
		}

		performExtraSmallOnlyRun := func() {
			log.Println("Start performing extra small runs...")

			for mainPlayer := 0; mainPlayer < len(nodesList); mainPlayer++ {
				runState.Wg.Add(2)
				log.Println("queue mainPlayer retriever run file_size: ", EXTRA_SMALL_SIZE)
				go e.DoRun(runState, key, mainPlayer, simplenode.Retriever, nodesList, EXTRA_SMALL_SIZE, 0)

				log.Println("queue mainPlayer publisher run file_size: ", EXTRA_SMALL_SIZE)
				go e.DoRun(runState, key, mainPlayer, simplenode.Publisher, nodesList, EXTRA_SMALL_SIZE, 0)

			}

		}

		performOtherSizesRun := func() {
			log.Println("Start performing other size runs...")

			for mainPlayer := 0; mainPlayer < len(nodesList); mainPlayer++ {
				runState.Wg.Add(6)
				log.Println("queue mainPlayer retriever run file_size: ", SMALL_SIZE)
				go e.DoRun(runState, key, mainPlayer, simplenode.Retriever, nodesList, SMALL_SIZE, 0)

				log.Println("queue mainPlayer retriever run file_size: ", MED_SIZE)
				go e.DoRun(runState, key, mainPlayer, simplenode.Retriever, nodesList, MED_SIZE, 0)

				log.Println("queue mainPlayer retriever run file_size: ", LARGE_SIZE)
				go e.DoRun(runState, key, mainPlayer, simplenode.Retriever, nodesList, LARGE_SIZE, 0)

				log.Println("queue mainPlayer publisher run file_size: ", SMALL_SIZE)
				go e.DoRun(runState, key, mainPlayer, simplenode.Publisher, nodesList, SMALL_SIZE, 0)

				log.Println("queue mainPlayer publisher run file_size: ", MED_SIZE)
				go e.DoRun(runState, key, mainPlayer, simplenode.Publisher, nodesList, MED_SIZE, 0)

				log.Println("queue mainPlayer publisher run file_size: ", LARGE_SIZE)
				go e.DoRun(runState, key, mainPlayer, simplenode.Publisher, nodesList, LARGE_SIZE, 0)

			}

		}

		// start invoking runs for each experiment type
		performDelayedRun()

		for i := 0; i < 3; i++ {
			performExtraSmallOnlyRun()
		}

		performOtherSizesRun()
		runState.Wg.Wait()
		if intervalSeconds == 0 {
			break
		}

		log.Printf("%d runs performed in this experiment\n", runState.Counter)
		log.Printf("%d experiments perfomed so far\n", numExperimentsPerformed)
		numExperimentsPerformed += 1
		time.Sleep(time.Duration(intervalSeconds) * time.Second)
	}
}
