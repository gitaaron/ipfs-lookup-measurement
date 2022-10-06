#!/bin/sh
echo "Updating nodes-list.out"
key=$(cat .key)
terraform refresh -var="KEY=$key"
sleep 5
terraform output > nodes-list.out
monitorIP=$(head -1 ./nodes-list.out | cut -d'"' -f2)
