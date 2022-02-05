#!/bin/bash


docker pull mviktorov/surv_server:latest
docker stop surv_server
docker rm -f surv_server
docker run --detach \
           --restart always \
           --publish 2121:2121 \
           --publish 60000-60300:60000-60300 \
           --name surv_server \
           -v /data/surv_server/.env:/.env \
           -v /data/surv_server/data:/data \
           mviktorov/surv_server:latest
