key:
	openssl rand 32 | base64 > node/.key
	cp -p node/.key controller/.key

docker: key docker-monitor docker-agent docker-controller docker-bootstrap

docker-monitor:
	cd monitor; docker build -t ipfs-monitor .; cd ..


docker-agent:
	rm -f controller/agent; docker build -t ipfs-node -f ./node/Dockerfile .

docker-controller:
	rm -f controller/controller
	rm -f controller/info
	docker build -t controller-node -f ./controller/Dockerfile .

docker-bootstrap:
	docker build -t bootstrap-node -f ./bootstrap/Dockerfile .
