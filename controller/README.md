# Controller

This project consists of two componets: an agent and controller.

The central controller instructs the IPFS instances, via the agents, to publish or retrieve carefully crafted CIDs into/from the network. 

Next to each IPFS instance an agent that can control the instance and in turn accepts commands by a central controller.

### Lookup Procedure

The controller starts with generating 0.5 of random data.

It then transfers this data to the first controlled IPFS instance and instructs it to announce to the IPFS network that it is in possession of this data.

This step resembles the content publication process.

As soon as this step has finished the controller instructs all remaining controlled IPFS instances to retrieve the CID of the random data.

This step involves finding the provider record, connecting to the provider (first controlled IPFS node) and then fetching the 0.5 of random data.

As soon as all remaining IPFS instances have completed this process the controller instructs them to disconnect from the provider.

This last step is done so that we avoid retrieving content through Bitswap during the next experiment, since peers would remain directly connected.

In other words, this would test the performance of Bitswap and not the DHT lookup process.


## Create a key

```shell
openssl rand 32 | base64 > .key
```

## Start ipfs for local testing
`ipfs daemon --init`
## Build
`make build`
## Integration testing with local ipfs
`make itest`
## Running simple nodes experiment
```
# editing nodes-list.out file with ipfs nodes, hostname:port
# run experiment
./controller

# or
./controller -l <nodes list file>

# or repeat test every X seconds
./controller -l <nodes list file> -i <interval in seconds>
```
