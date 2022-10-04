package main

import (
	"encoding/base64"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"time"
  "math"

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
	ids := make([]string, 0)
	for _, node := range nodesList {
		fmt.Printf("Start asking for node id from %v\n", node)
		id, err := server.RequestGetID(node.Host(), key)
		if err != nil {
			fmt.Printf("error getting node id for %v: %v\n", node, err.Error())
			return
		}
		fmt.Printf("Got node id for %v: %v\n", node, id)
		ids = append(ids, id)
	}
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

	// Start the experiment.

	for {

		e := simplenode.NewExperiment()

    // 0.05 MB
    extra_small_size := int(math.Round(0.05*1024*1024))
    // ~0.5 MB
    small_size := extra_small_size*10
    // ~5 MB
    med_size := small_size*10
    // ~50 MB
    large_size := med_size*10

    performExtraSmallOnlyRun := func() {

      for mainPlayer := 0; mainPlayer < len(nodesList); mainPlayer++ {

        log.Println("start mainPlayer retriever run file_size: ", extra_small_size)
        e.DoRun(key, mainPlayer, simplenode.Retriever, nodesList, extra_small_size)

        log.Println("start mainPlayer publisher run file_size: ", extra_small_size)
        e.DoRun(key, mainPlayer, simplenode.Publisher, nodesList, extra_small_size)

        log.Println("one retrieval and publish run is done for node: ", mainPlayer)

      }

    }

    performOtherSizesRun := func() {

      for mainPlayer := 0; mainPlayer < len(nodesList); mainPlayer++ {

        log.Println("start mainPlayer retriever run file_size: ", small_size)
        e.DoRun(key, mainPlayer, simplenode.Retriever, nodesList, small_size)

        log.Println("start mainPlayer retriever run file_size: ", med_size)
        e.DoRun(key, mainPlayer, simplenode.Retriever, nodesList, med_size)

        log.Println("start mainPlayer retriever run file_size: ", large_size)
        e.DoRun(key, mainPlayer, simplenode.Retriever, nodesList, large_size)

        log.Println("start mainPlayer publisher run file_size: ", small_size)
        e.DoRun(key, mainPlayer, simplenode.Publisher, nodesList, small_size)

        log.Println("start mainPlayer publisher run file_size: ", med_size)
        e.DoRun(key, mainPlayer, simplenode.Publisher, nodesList, med_size)

        log.Println("start mainPlayer publisher run file_size: ", large_size)
        e.DoRun(key, mainPlayer, simplenode.Publisher, nodesList, large_size)

        log.Println("one retrieval and publish experiment is done for node:", mainPlayer)

      }

    }

    for i := 0; i < 6; i++ {
      performExtraSmallOnlyRun()
    }

    performOtherSizesRun()

		log.Println("one round of experiments is done")

		if *intervalSeconds == 0 {
			break
		}

		time.Sleep(time.Duration(*intervalSeconds) * time.Second)
	}
}
