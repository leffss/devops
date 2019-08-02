#!/bin/bash

docker rm -f devops
docker rmi -f devops

docker build -t devops .
docker run -d --name devops -p 8000:8000 devops
