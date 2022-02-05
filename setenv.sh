#!/bin/bash


export DOCKER_IMAGE_TAG=surv_server:latest


if [[ -f "setenv_local.sh" ]]; then
  source setenv_local.sh
fi
