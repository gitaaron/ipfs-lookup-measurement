#!/bin/sh
./controller/info
mv agent_info.json ./analysis/agent_info.json
IPFS_LOGGING=INFO ./controller/controller -i 60
