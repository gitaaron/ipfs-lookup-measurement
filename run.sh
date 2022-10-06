#!/bin/sh
RESTART_AGENTS=./restart_agents.cmd
STOP_EXPERIMENT=./stop_experiment.cmd
./controller/info
mv agent_info.json ./analysis/agent_info.json
counter=0
while true
do
	if test -f "$STOP_EXPERIMENT"; then
		echo "stopping experiment..."
		rm "$STOP_EXPERIMENT"
		exit 0
	fi
	if test -f "$RESTART_AGENTS"; then
		echo "restarting agents..."
		rm "$RESTART_AGENTS"
		./restart_agents.sh
	fi
	IPFS_LOGGING=INFO ./controller/controller
	echo "$counter experiment(s) completed..."
	counter=$((counter+1))
	sleep 5
done
