#!/bin/sh
key=$(cat .key)
terraform destroy -auto-approve -target="module.testing_node_0" -target="module.testing_node_1" -target="module.testing_node_2" -target="module.testing_node_3" -target="module.testing_node_4" -target="module.testing_node_5" -var="KEY=$key"
terraform apply -auto-approve -var="KEY=$key"
sleep 5
terraform output > nodes-list.out
