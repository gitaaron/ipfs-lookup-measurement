#!/usr/bin/env bash
export LOKI_ADDR="http://$(terraform output -raw monitor_ip):3100"
echo $LOKI_ADDR
python3 collect/download_logs.py
