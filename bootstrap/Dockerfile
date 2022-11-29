FROM ubuntu:18.04
WORKDIR /app
RUN apt-get update && apt-get install -y wget unzip tar git make build-essential
RUN wget https://golang.org/dl/go1.18.1.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.18.1.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

RUN git clone https://github.com/dennis-tra/go-libp2p-kad-dht.git && cd go-libp2p-kad-dht && git checkout v0.18.0-more-logging && cd ..
RUN git clone https://github.com/dennis-tra/go-bitswap.git && cd go-bitswap && git checkout v0.10.2-more-logging && cd ..
RUN git clone https://github.com/dennis-tra/go-ipfs.git  && cd go-ipfs && git checkout v0.17.0-more-logging && echo "replace github.com/libp2p/go-libp2p-kad-dht => ../go-libp2p-kad-dht" >> go.mod && echo "replace github.com/libp2p/go-bitswap => ../go-bitswap" >> go.mod && make build

COPY ./bootstrap /app/bootstrap
WORKDIR /app/
CMD [ "./bootstrap/docker-entrypoint.sh" ]
