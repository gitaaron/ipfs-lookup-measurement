BOOTSTRAP_ID_0=$(docker exec -it -e IPFS_LOGGING=INFO bootstrap0 /app/go-ipfs/cmd/ipfs/ipfs id -f="<id>")
BOOTSTRAP_ID_1=$(docker exec -it -e IPFS_LOGGING=INFO bootstrap1 /app/go-ipfs/cmd/ipfs/ipfs id -f="<id>")
BOOTSTRAP_ID_2=$(docker exec -it -e IPFS_LOGGING=INFO bootstrap2 /app/go-ipfs/cmd/ipfs/ipfs id -f="<id>")

docker exec -it bootstrap0 /app/go-ipfs/cmd/ipfs/ipfs bootstrap add /dns4/bootstrap1/tcp/4101/p2p/$BOOTSTRAP_ID_1
docker exec -it bootstrap1 /app/go-ipfs/cmd/ipfs/ipfs bootstrap add /dns4/bootstrap2/tcp/4102/p2p/$BOOTSTRAP_ID_2
docker exec -it bootstrap2 /app/go-ipfs/cmd/ipfs/ipfs bootstrap add /dns4/bootstrap0/tcp/4100/p2p/$BOOTSTRAP_ID_0

docker exec -it node0 /app/kubo/cmd/ipfs/ipfs bootstrap add /dns4/bootstrap0/tcp/4100/p2p/$BOOTSTRAP_ID_0
docker exec -it node1 /app/kubo/cmd/ipfs/ipfs bootstrap add /dns4/bootstrap1/tcp/4101/p2p/$BOOTSTRAP_ID_1
docker exec -it node2 /app/kubo/cmd/ipfs/ipfs bootstrap add /dns4/bootstrap2/tcp/4102/p2p/$BOOTSTRAP_ID_2
