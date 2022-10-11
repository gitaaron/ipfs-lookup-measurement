package server

import (
	"fmt"
	"time"

	linuxproc "github.com/c9s/goprocinfo/linux"
)

func LogHealthPeriodically() {

	go func() {
		for {

			meminfo, err := linuxproc.ReadMemInfo("/proc/meminfo")

			if err != nil {
				log.Fatal("mem read failed")
			}

			loadavg, err := linuxproc.ReadLoadAvg("/proc/loadavg")

			if err != nil {
				log.Fatal("uptime read failed")
			}

			fmt.Printf("%s: available_mem:%v load_avg_last_min:%v\n", time.Now().Format(time.RFC3339Nano), meminfo.MemAvailable, loadavg.Last1Min)

			time.Sleep(5 * time.Minute)
		}
	}()
}