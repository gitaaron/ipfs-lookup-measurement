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
: "${PERFORMANCE_TEST_DIR:=/ipfs-tests}"

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
