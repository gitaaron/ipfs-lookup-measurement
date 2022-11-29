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

set -e
: "${IPFS_LOGGING}:=INFO"

./go-ipfs/cmd/ipfs/ipfs init
./go-ipfs/cmd/ipfs/ipfs config Addresses.API "/ip4/127.0.0.1/tcp/$SERVER_PORT"
./go-ipfs/cmd/ipfs/ipfs config Addresses.Gateway "/ip4/127.0.0.1/tcp/$GATEWAY_PORT"
./go-ipfs/cmd/ipfs/ipfs config --json Addresses.Swarm "[\
  \"/ip4/0.0.0.0/tcp/$P2P_PORT\"
]"

./go-ipfs/cmd/ipfs/ipfs config AutoNAT.ServiceMode "disabled"
./go-ipfs/cmd/ipfs/ipfs config --json Discovery.MDNS.Enabled false

./go-ipfs/cmd/ipfs/ipfs bootstrap rm --all

./go-ipfs/cmd/ipfs/ipfs daemon | tee /app/all.log &

sleep infinity
