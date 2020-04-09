#!/bin/bash

path=$(pwd)
docker rm -f devops
docker rmi -f devops
rm -rf logs/*
docker build -t devops .

docker run -d --name devops -p 8000:8000 -p 8001:8001 -p 2222:2222 -v ${path}:/devops -v /etc/localtime:/etc/localtime devops:latest

# docker run -d --name devops -P devops
