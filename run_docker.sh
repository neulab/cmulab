#!/bin/bash

[ $# -ne 1 ] && { echo "$0 docker_image_tag"; exit 1; }
tag=$1
docker run -it --name cmulab-devel-run-$tag -v /path/to/config/:/config/ -p 8088:8088 zs12/cmulab-devel:$tag /bin/bash
# manually run 
# GOOGLE_APPLICATION_CREDENTIALS=/config/google_credentials.json ./start.sh
