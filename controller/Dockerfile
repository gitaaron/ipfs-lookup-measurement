FROM ubuntu:18.04
WORKDIR /app
RUN apt-get update && apt-get install -y wget unzip tar git make build-essential
RUN wget https://golang.org/dl/go1.17.1.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.17.1.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

RUN mkdir /ipfs-tests/
COPY ./.key /ipfs-tests/
COPY ./controller /app/controller
WORKDIR /app/controller
RUN make controller
RUN mv nodes-list.out.docker nodes-list.out

WORKDIR /app
CMD [ "./controller/docker-entrypoint.sh" ]
