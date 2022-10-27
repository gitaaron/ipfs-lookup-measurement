// simplenode package will test with ipfs api
package simplenode

import (
	"crypto/rand"
	"errors"
	"fmt"
	"sync"
	"time"

	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/config"
	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/server"

	logging "github.com/ipfs/go-log"
)

var log = logging.Logger("controller")

type PlayerType int

// mu is a lock so that other runs can proceed while
// the delayed run is waiting before the second part completes
// wg is to let the calling controller know when the run is complete
// counter is to track how many runs have completed
type RunState struct {
	mu      sync.Mutex
	Wg      sync.WaitGroup
	Counter int
}

type FirstPartResult struct {
	cid string
	err error
}

const (
	Retriever PlayerType = iota
	Publisher
)

type Experiment struct{}

func NewExperiment() *Experiment {
	return &Experiment{}
}

func (exp Experiment) doRetrieve(key []byte, cid string, fileSize int, retrieverNode string) {
	// First do a disconnection to avoid using bitswap
	out, err := server.RequestDisconnect(retrieverNode, key)
	if err != nil {
		log.Errorf("Error requesting disconnection to %v: %v", retrieverNode, err.Error())
		return
	}
	log.Infof("Response of disconnection from %v is: %v", retrieverNode, out)
	log.Infof("Start lookup %v from %v", cid, retrieverNode)

	err = server.RequestLookup(retrieverNode, key, server.SendFile{Cid: cid, Size: fileSize})

	if err != nil {
		log.Errorf("Error requesting lookup to %v: %v", retrieverNode, err.Error())
		return
	}
	// Need to wait till lookup is finished.
	for i := 0; i < 30; i++ {
		time.Sleep(5000 * time.Millisecond)
		done, err := server.RequestCheck(retrieverNode, key, cid)
		if err != nil {
			log.Errorf("Error in requesting a check to %v: %v", retrieverNode, err.Error())
			return
		}
		if done {
			log.Infof("Lookup from %v is done", retrieverNode)
			break
		}
		if i == 29 {
			log.Errorf("Error in lookup from %v", retrieverNode)
			return
		}
		log.Infof("Lookup from %v in progress...", retrieverNode)
	}
}

func (exp *Experiment) doPublish(key []byte, content *[]byte, publisherNode string) (string, error) {
	// Request Publish
	// First do a disconnection to avoid using bitswap
	out, err := server.RequestDisconnect(publisherNode, key)
	if err != nil {
		log.Errorf("Error in performing 'RequestDisconnect'")
		return "", err
	}
	log.Infof("Response of disconnection from %v is: %v", publisherNode, out)
	cid, err := server.RequestPublish(publisherNode, key, *content)
	if err != nil {
		log.Errorf("Error in performing 'RequestPublish'")
		return "", err
	}

	log.Infof("Published content from %v with cid: %v", publisherNode, cid)
	// Need to wait till publish is finished.
	for i := 0; i < 60; i++ {
		time.Sleep(5000 * time.Millisecond)
		done, err := server.RequestCheck(publisherNode, key, cid)
		if err != nil {
			log.Errorf("Error in performing 'RequestCheck'")
			return "", err
		}
		if done {
			log.Infof("Publish from %v is done", publisherNode)
			break
		}
		if i == 59 {
			return "", errors.New("timing out on publish OK check")
		}
		log.Infof("Publish from %v in progress...", publisherNode)
	}

	return cid, nil
}

func (exp *Experiment) doFirstPartOfRun(result chan FirstPartResult, key []byte, mainPlayerIndex int, mainPlayerMode PlayerType, nodesList []config.AgentNode, size int) {
	log.Infof("Start first part mainPlayerIndex: %d mainPlayerMode: %v size:%d", mainPlayerIndex, mainPlayerMode, size)
	mainPlayer := nodesList[mainPlayerIndex].Host()

	// Generate random content
	content := make([]byte, size)
	rand.Read(content)

	var cid string
	var err error
	var wg sync.WaitGroup

	if mainPlayerMode != Publisher && mainPlayerMode != Retriever {
		result <- FirstPartResult{"", fmt.Errorf("invalid mainPlayerMode %v", mainPlayerMode)}
	}

	// Start publish to appropriate nodes
	if mainPlayerMode == Publisher {
		cid, err = exp.doPublish(key, &content, mainPlayer)
		if err != nil {
			result <- FirstPartResult{"", fmt.Errorf("error in performing 'doPublish' from %v: %v", mainPlayer, err.Error())}
		}
	} else if mainPlayerMode == Retriever {
		// experiment should continue only if two or more nodes succeeded in publishing the 'file'
		publishSuccessCount := 0

		for i, publisher := range nodesList {
			if i == mainPlayerIndex {
				continue
			}
			wg.Add(1)
			go func(wg *sync.WaitGroup, publisher string) {
				defer wg.Done()
				cid, err = exp.doPublish(key, &content, publisher)
				if err != nil {
					log.Errorf("error in performing 'doPublish' from %v: %v", mainPlayer, err.Error())
				} else {
					publishSuccessCount += 1
				}
			}(&wg, publisher.Host())
		}
		wg.Wait()

		if publishSuccessCount < 2 {
			result <- FirstPartResult{"", fmt.Errorf("discontinuing experiment because less than two nodes published the 'file' successfully")}
		}

	}

	result <- FirstPartResult{cid, nil}

}

func (exp *Experiment) doSecondPartOfRun(secondPartWait *sync.WaitGroup, cid string, key []byte, mainPlayerIndex int, mainPlayerMode PlayerType, nodesList []config.AgentNode, size int) {
	defer secondPartWait.Done()
	log.Infof("Start second part cid: %s mainPlayerIndex: %d mainPlayerMode: %v", cid, mainPlayerIndex, mainPlayerMode)
	mainPlayer := nodesList[mainPlayerIndex].Host()
	var wg sync.WaitGroup

	// Start lookup from appropriate nodes
	if mainPlayerMode == Publisher {
		for i, retriever := range nodesList {
			if i == mainPlayerIndex {
				continue
			}
			wg.Add(1)
			go func(wg *sync.WaitGroup, retriever string) {
				defer wg.Done()
				exp.doRetrieve(key, cid, size, retriever)
			}(&wg, retriever.Host())
		}
		wg.Wait()
		log.Infof("all retrieves are done")
	} else if mainPlayerMode == Retriever {
		exp.doRetrieve(key, cid, size, mainPlayer)
	}

	// Clean
	for _, node := range nodesList {
		wg.Add(1)
		go func(wg *sync.WaitGroup, node string) {
			defer wg.Done()
			out, err := server.RequestClean(node, key, cid)
			if err != nil {
				log.Errorf("Error in requesting clean of %v to %v: %v", cid, node, err.Error())
			} else {
				log.Infof("Response of clean of %v from %v is: %v", cid, node, out)
			}
		}(&wg, node.Host())
	}
	wg.Wait()
	log.Infof("clean is done")
}

// DoRun instructs a set of nodes to publish a random 'file' and another set of nodes to retrieve it
// the action of the mainPlayer is either a publisher or retriever based on mainPlayerMode
// the rest of the nodes in the nodesList will act as the other PlayerType in the scenario
func (exp *Experiment) DoRun(runState *RunState, key []byte, mainPlayerIndex int, mainPlayerMode PlayerType, nodesList []config.AgentNode, size int, delay int) {
	defer runState.Wg.Done()
	runState.mu.Lock()
	resultChan := make(chan FirstPartResult)
	go exp.doFirstPartOfRun(resultChan, key, mainPlayerIndex, mainPlayerMode, nodesList, size)
	result := <-resultChan
	if result.err != nil {
		log.Error(result.err)
		runState.mu.Unlock()
		return
	}

	cid := result.cid

	if delay > 0 {
		log.Infof("Sleeping for %d seconds before performing second part", delay)
		runState.mu.Unlock()
		time.Sleep(time.Duration(delay) * time.Second)
		runState.mu.Lock()
	}

	var wg sync.WaitGroup
	wg.Add(1)
	exp.doSecondPartOfRun(&wg, cid, key, mainPlayerIndex, mainPlayerMode, nodesList, size)
	wg.Wait()
	runState.Counter++
	runState.mu.Unlock()

}
