FROM ubuntu:18.04
WORKDIR /app
RUN apt-get update && apt-get install -y wget unzip tar git make build-essential
RUN wget https://golang.org/dl/go1.17.1.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.17.1.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

RUN git clone https://github.com/gitaaron/go-libp2p-kad-dht.git && cd go-libp2p-kad-dht && git checkout more-logging && cd ..
RUN git clone https://github.com/gitaaron/go-bitswap.git && cd go-bitswap && git checkout more-logging && cd ..
RUN git clone https://github.com/gitaaron/kubo.git  && cd kubo && git checkout more-logging && echo "replace github.com/libp2p/go-libp2p-kad-dht => ../go-libp2p-kad-dht" >> go.mod && echo "replace github.com/libp2p/go-bitswap => ../go-bitswap" >> go.mod && make build


COPY ./controller /app/controller
WORKDIR /app/controller
RUN make controller
RUN make info
RUN mv nodes-list.out.docker /app/nodes-list.out
COPY ./run.sh /app
RUN mv /app/controller/.key /app
RUN mkdir /app/analysis
RUN mv /app/controller/restart_agents.sh.docker /app/restart_agents.sh

WORKDIR /app
CMD [ "./controller/docker-entrypoint.sh" ]
