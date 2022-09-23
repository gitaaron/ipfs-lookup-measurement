// simplenode package will test with ipfs api
package simplenode

import (
	"crypto/rand"
	"sync"
	"time"
  "errors"

	"github.com/gitaaron/ipfs-lookup-measurement/controller/pkg/server"
	logging "github.com/ipfs/go-log"
)

var log = logging.Logger("controller")

type PlayerType int

const (
  Retriever PlayerType = iota
  Publisher
)

type Experiment struct { }

func NewExperiment() *Experiment {
  return &Experiment{}
}

func (exp Experiment) doRetrieve(key []byte, cid string, retrieverNode string) {
  // First do a disconnection to avoid using bitswap
  out, err := server.RequestDisconnect(retrieverNode, key)
  if err != nil {
    log.Errorf("Error requesting disconnection to %v: %v", retrieverNode, err.Error())
    return
  }
  log.Infof("Response of disconnection from %v is: %v", retrieverNode, out)
  log.Infof("Start lookup %v from %v", cid, retrieverNode)
  err = server.RequestLookup(retrieverNode, key, cid)
  if err != nil {
    log.Errorf("Error requesting lookup to %v: %v", retrieverNode, err.Error())
    return
  }
  // Need to wait till lookup is finished.
  for i := 0; i < 30; i++ {
    time.Sleep(5 * time.Second)
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
		time.Sleep(5 * time.Second)
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
			return "", errors.New("Timing out on publish OK check.")
		}
		log.Infof("Publish from %v in progress...", publisherNode)
	}

  return cid, nil
}

// DoRun instructs a set of nodes to publish a random 'file' and another set of nodes to retrieve it
// the action of the mainPlayer is either a publisher or retriever based on mainPlayerMode
// the rest of the nodes in the nodesList will act as the other PlayerType in the scenario
func (exp *Experiment) DoRun(key []byte, mainPlayerIndex int, mainPlayerMode PlayerType, nodesList []string) {
	mainPlayer := nodesList[mainPlayerIndex]

	// Generate random content, 0.5 MB.
	content := make([]byte, 500_000)
	rand.Read(content)

  var cid string
  var err error
	var wg sync.WaitGroup


	// Start publish to appropriate nodes
  if(mainPlayerMode==Publisher) {
    cid, err = exp.doPublish(key, &content, mainPlayer)
    if err != nil {
      log.Errorf("Error in performing 'doPublish' from %v: %v", mainPlayer, err.Error())
      return
    }

    // Start lookup from appropriate nodes
    for i, retriever := range nodesList {
      if i == mainPlayerIndex {
        continue
      }
      wg.Add(1)
      go func(wg *sync.WaitGroup, retriever string) {
        defer wg.Done()
        exp.doRetrieve(key, cid, retriever)
      }(&wg, retriever)
    }
    wg.Wait()
    log.Infof("all retrieves are done")


  } else if(mainPlayerMode==Retriever) {
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
          log.Errorf("Error in performing 'doPublish' from %v: %v", mainPlayer, err.Error())
        } else {
          publishSuccessCount += 1
        }
      }(&wg, publisher)
    }
    wg.Wait()
    if(publishSuccessCount < 2) {
      log.Error("Discontinuing experiment because less than two nodes published the 'file' successfully")
      return
    }

    exp.doRetrieve(key, cid, mainPlayer)

  } else {
    log.Errorf("Invalid mainPlayerMode %s", mainPlayerMode)
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
		}(&wg, node)
	}
	wg.Wait()
	log.Infof("clean is done")
}
