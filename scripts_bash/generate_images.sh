#!/bin/bash

cd docker_management/
docker stop $(docker ps -a -q); 
docker rm -f $(docker ps -a -q); 
docker rmi -f $(docker images -q); 
python3 docker_image_tuxml.py -f
cd ../
