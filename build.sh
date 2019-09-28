#!/bin/bash
source ./deployment/.env

APP_NAME="recruiter_bot"

docker build . -f ./deployment/Dockerfile \
    -t $APP_NAME \

docker rm -f $(docker ps -aq --filter name=$APP_NAME)
docker run -d -p $APPLICATION_PORT:$APPLICATION_PORT \
    --env "PRODUCTION=True"\
    --env-file=./deployment/.env \
    --name $APP_NAME \
    $APP_NAME
