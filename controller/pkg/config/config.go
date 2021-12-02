package config

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strings"
)

func GetNodesList(nodesListFile string) []string {
	f, err := os.Open(nodesListFile)
	if err != nil {
		log.Fatalln(err)
	}

	// Create new Scanner.
	scanner := bufio.NewScanner(f)
	result := []string{}

	// Use Scan.
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		// Append line to result.
		if line != "" && !strings.HasPrefix(line, "monitor") {
			parts := strings.Split(line, "\"")
			if len(parts) > 1 {
				result = append(result, fmt.Sprintf("http://%v:3030", parts[1]))
			} else {
				result = append(result, line)
			}
		}
	}

	if len(result) == 0 {
		log.Fatalln("nodes list file is empty")
	}
	return result
}
