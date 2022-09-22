key:
	openssl rand 32 | base64 > node/.key
	cp -p node/.key controller/.key

docker: key docker-monitor docker-agent docker-controller

docker-monitor:
	cd monitor; docker build -t ipfs-monitor .; cd ..


docker-agent:
	rm -f node/agent; docker build -t ipfs-node -f ./node/Dockerfile .

docker-controller:
	rm -f node/controller; docker build -t controller-node -f ./controller/Dockerfile .
