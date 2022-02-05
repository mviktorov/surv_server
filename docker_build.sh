#!/bin/bash

source setenv.sh
docker build -t ${DOCKER_IMAGE_TAG} .
