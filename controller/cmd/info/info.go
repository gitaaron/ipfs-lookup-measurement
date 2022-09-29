package main

import (
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"os"

	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/config"
	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/server"
)

func main() {
	simpleNodesFile := flag.String("l", "nodes-list.out", "nodes list file")

	flag.Parse()
	nodesList, err := config.GetNodesList(*simpleNodesFile)

	if err != nil {
		fmt.Printf("failed to get nodes list: %v", err)
		return
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
	for i, node := range nodesList {
		fmt.Printf("Start asking for node id from %v\n", node.Host())
		id, err := server.RequestGetID(node.Host(), key)
		if err != nil {
			fmt.Printf("error getting node id for %v: %v\n", node, err.Error())
			return
		}
		nodesList[i].Peer_ID = id
	}

	jsonString, err := json.MarshalIndent(nodesList, "", "  ")
	if err != nil {
		fmt.Printf("failed to marshal nodesList to json: %+v", nodesList)
	}

	f_err := os.WriteFile("./agent_info.json", jsonString, 0644)

	if f_err == nil {
		fmt.Printf("wrote to ./agent_info.json")
	} else {
		panic(err)
	}

}
