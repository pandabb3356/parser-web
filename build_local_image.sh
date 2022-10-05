#!/bin/bash

set -e

REGISTRY=''

IMAGE_VERSION=${IMAGE_VERSION}

PARSER_WEB_IMAGE_NAME="${REGISTRY}parser-web"
PARSER_WEB_FRONTEND_IMAGE_NAME="${REGISTRY}parser-web-frontend"

PARSER_WEB_IMAGE_NAME+=:${IMAGE_VERSION}
PARSER_WEB_FRONTEND_IMAGE_NAME+=:${IMAGE_VERSION}

docker build -t $PARSER_WEB_IMAGE_NAME -f Dockerfile .
docker build -t $PARSER_WEB_FRONTEND_IMAGE_NAME -f docker/frontend/Dockerfile .
