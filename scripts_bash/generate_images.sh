#!/bin/bash

cd docker_management/
# Commented for securty reasons, to use only if necessary and never in production :
# docker stop $(docker ps -a -q); 
# docker rm -f $(docker ps -a -q); 
# docker rmi $(docker images | grep 'tuxml/')
# docker image prune -f
python3 docker_image_tuxml.py -f
cd ../
