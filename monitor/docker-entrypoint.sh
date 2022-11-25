#!/bin/sh

# Start loki
./loki-linux-amd64 -config.file=loki-local-config.yaml &
# Start grafana
cd ./grafana-8.5.6/bin
./grafana-server
