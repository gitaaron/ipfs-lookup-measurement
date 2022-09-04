docker: key docker-monitor docker-agent

key:
	openssl rand 32 | base64 > node/.key
	cp -p node/.key controller/.key


docker-monitor:
	cd monitor; docker build -t ipfs-monitor .; cd ..


docker-agent:
	docker build -t ipfs-node -f ./node/Dockerfile .

