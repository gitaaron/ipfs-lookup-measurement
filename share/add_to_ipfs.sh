#!/usr/bin/env sh
cid=$(ipfs add -Qr --only-hash build)
echo $cid
ipfs name publish --key=dht_lookup_key /ipfs/$cid
