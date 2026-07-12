#!/usr/bin/env bash
# Builds the Docker image for the EasyRAG bot from the local Dockerfile.
docker build -t easyrag:latest -f Dockerfile .
