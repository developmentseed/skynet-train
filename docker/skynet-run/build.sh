#!/usr/bin/env bash

docker build -t developmentseed/skynet-run:gpu -f docker/skynet-run/Dockerfile.gpu .
docker build -t developmentseed/skynet-run:cpu -f docker/skynet-run/Dockerfile.cpu .

