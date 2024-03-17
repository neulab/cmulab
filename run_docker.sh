#!/bin/bash

[ $# -ne 1 ] && { echo "$0 docker_image_tag"; exit 1; }
tag=$1
set -x
#docker run -it --name cmulab-devel-run-$tag -v /path/to/config/:/config/ -p 8088:8088 zs12/cmulab-devel:$tag /bin/bash
docker run -it -p 8088:8088 \
  -v /usr1/data/zsheikh/DSTA-project/.config:/dev/shm/.config/ \
  -v /usr1/data/zsheikh/DSTA-project/cmulab_annotator_media/:/cmulab/annotator/media/ \
  --name cmulab-devel-$tag \
  zs12/cmulab-devel:$tag /bin/bash
