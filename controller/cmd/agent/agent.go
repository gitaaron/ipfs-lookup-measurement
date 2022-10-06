package main

import (
	"context"
	"flag"
	"fmt"
	"io/ioutil"
	"os"

	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/server"
)

func main() {
	ipfsTestFolder := os.Getenv("PERFORMANCE_TEST_DIR")
	if ipfsTestFolder == "" {
		ipfsTestFolder = "/ipfs-tests"
	}

	err := os.Chdir(ipfsTestFolder)
	if err != nil {
		fmt.Printf("error in chdir: %v\n", err.Error())
		return
	}

	hostStr := flag.String("host", "", "host")
	portNumStr := flag.String("port", "3030", "port number")
	flag.Parse()
	key, err := ioutil.ReadFile(".key")
	if err != nil {
		fmt.Printf("error in getting the key: %v\n", err.Error())
		return
	}

	server.NewServer(context.Background(), *hostStr+":"+*portNumStr, string(key))
}
