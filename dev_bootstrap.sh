CONTROLLER_ID=$(docker exec -it controller /app/kubo/cmd/ipfs/ipfs id -f="<id>")
docker exec -it node0 /app/kubo/cmd/ipfs/ipfs bootstrap add /dns4/controller/tcp/4100/p2p/$CONTROLLER_ID
docker exec -it node1 /app/kubo/cmd/ipfs/ipfs bootstrap add /dns4/controller/tcp/4100/p2p/$CONTROLLER_ID
docker exec -it node2 /app/kubo/cmd/ipfs/ipfs bootstrap add /dns4/controller/tcp/4100/p2p/$CONTROLLER_ID
