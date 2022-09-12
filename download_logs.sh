#!/usr/bin/env bash
LOKI_ADDR="http://$(terraform output -raw monitor_ip):3100"
echo $LOKI_ADDR
python3 analysis/download_logs.py
