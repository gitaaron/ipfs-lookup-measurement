# Controller

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
