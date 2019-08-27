#!/bin/bash

docker rm -f devops
docker rmi -f devops

docker build -t devops .

docker run -d --name devops -p 8000:8000 -p 2222:2222 devops

# docker run -d --name devops -P devops
