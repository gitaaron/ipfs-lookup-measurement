#!/bin/sh

key=$(cat .key)
terraform destroy \
	-target="module.testing_node_0" \
	-target="module.testing_node_1" \
	-target="module.testing_node_2" \
	-target="module.testing_node_3" \
	-target="module.testing_node_4" \
	-target="module.testing_node_5" \
	-target="module.testing_node_6" \
	-var="KEY=$key"
