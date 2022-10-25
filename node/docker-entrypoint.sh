#!/usr/bin/env sh

set -e
: "${HOST_NAME:=node-undefined}"

set -e
: "${P2P_PORT:=4001}"

set -e
: "${SERVER_PORT:=5001}"

set -e
: "${GATEWAY_PORT:=8080}"

set -e
: "${AGENT_PORT:=3030}"

set -e
: "${AGENT_HOST:=127.0.0.1}"

set -e
: "${PERFORMANCE_TEST_DIR:=/ipfs-tests}"


# Start loki
echo "      host: $HOST_NAME" >> promtail-local-config.yaml
./promtail-linux-amd64 -config.file=promtail-local-config.yaml &

# Start agent
echo "PERF $PERFORMANCE_TEST_DIR"

IPFS=/app/kubo/cmd/ipfs/ipfs IPFS_LOGGING=INFO ./agent -host=$AGENT_HOST -port=$AGENT_PORT 2>&1 | tee /app/agent.log &
./kubo/cmd/ipfs/ipfs init
./kubo/cmd/ipfs/ipfs config Addresses.API "/ip4/127.0.0.1/tcp/$SERVER_PORT"
./kubo/cmd/ipfs/ipfs config Addresses.Gateway "/ip4/127.0.0.1/tcp/$GATEWAY_PORT"
./kubo/cmd/ipfs/ipfs config --json Addresses.Swarm "[\
  \"/ip4/0.0.0.0/tcp/$P2P_PORT\",\
  \"/ip6/::/tcp/$P2P_PORT\",\
  \"/ip4/0.0.0.0/udp/$P2P_PORT/quic\",\
  \"/ip6/::/udp/$P2P_PORT/quic\"\
]"

./kubo/cmd/ipfs/ipfs config --json Discovery.MDNS.Enabled false

./kubo/cmd/ipfs/ipfs bootstrap rm --all

./kubo/cmd/ipfs/ipfs daemon | tee /app/all.log &

sleep infinity
