package config

import (
	"bufio"
	"errors"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
)

type AgentNode struct {
	Public_ip  string
	Port       string
	Region_key string
	Node_num   int
	Peer_ID    string
}

func (an *AgentNode) Host() string {
	return fmt.Sprintf("http://%v:%v", an.Public_ip, an.Port)
}

func GetNodesList(nodesListFile string) ([]AgentNode, error) {
	f, err := os.Open(nodesListFile)
	if err != nil {
		return nil, err
	}

	// Create new Scanner.
	scanner := bufio.NewScanner(f)

	node_nums_val_map := make(map[int]map[string]string)

	// Use Scan.
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		// Append line to result.
		if line != "" && !strings.HasPrefix(line, "monitor") {
			parts := strings.Split(line, "=")
			if len(parts) > 1 {
				key := strings.TrimSpace(parts[0])
				value := strings.TrimSpace(strings.Split(parts[1], "\"")[1])
				key_parts := strings.Split(key, "_")

				str_node_num := key_parts[1]
				node_num, err := strconv.Atoi(str_node_num)
				if err != nil {
					log.Printf("node_num is not a number %s\n", str_node_num)
					continue
				}
				key_type := key_parts[2]

				if node_nums_val_map[node_num] == nil {
					node_nums_val_map[node_num] = make(map[string]string)
				}

				if key_type == "ip" {
					node_nums_val_map[node_num]["ip"] = value
				} else if key_type == "arn" {
					node_nums_val_map[node_num]["arn"] = value
				} else if key_type == "port" {
					node_nums_val_map[node_num]["port"] = value
				} else {
					log.Printf("unknown key type: (%v)\n", key_type)
					continue
				}

			} else {
				log.Printf("skipping line: %v parts: %d\n", line, len(parts))
				continue
			}

		}
	}

	agent_nodes := []AgentNode{}

	for node_num, node := range node_nums_val_map {

		if node["ip"] == "" {
			log.Printf("node missing ip %d : %v\n", node_num, node)
			continue
		}

		if node["arn"] == "" {
			log.Printf("node missing arn %d : %v\n", node_num, node)
			continue
		}

		if node["port"] == "" {
			node["port"] = "3030"
		}

		region_key := strings.ReplaceAll(strings.Split(node["arn"], ":")[3], "-", "_")

		an := AgentNode{
			Public_ip:  node["ip"],
			Port:       node["port"],
			Region_key: region_key,
			Node_num:   node_num}

		agent_nodes = append(agent_nodes, an)
	}

	if len(agent_nodes) == 0 {
		return nil, errors.New("nodes list file is empty")
	}

	return agent_nodes, nil
}
