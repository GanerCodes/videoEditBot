#!/bin/bash
set -e
docker image rm -f videoeditbot
docker build . -t videoeditbot
(docker stop videoeditbot ; docker rm videoeditbot) || :
docker run -dt --restart=always --cpus=".75" --name videoeditbot --network host videoeditbot
