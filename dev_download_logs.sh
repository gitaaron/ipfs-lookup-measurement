#!/usr/bin/env bash
export LOKI_ADDR="http://localhost:3100"
export NODE_LIST=node0,node1,node2
export DOWNLOAD_DIR=output
SINCE=24 python3 collect/download_logs.py
