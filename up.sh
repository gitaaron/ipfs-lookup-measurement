#!/bin/sh

key=$(cat .key)
terraform apply -var="KEY=$key"
sleep 5
terraform output > nodes-list.out
monitorIP=$(head -1 ./nodes-list.out | cut -d'"' -f2)
echo "monitor URL is $monitorIP:3000"
