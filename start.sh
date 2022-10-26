#!/bin/bash


eval $(conda shell.bash hook)
conda activate cmulab
source activate cmulab
set -x

pkill -f rqworker
pkill -f runserver
pkill -f redis-server

cd $(readlink -f $(dirname $0))
python manage.py makemigrations annotator
python manage.py migrate
export PYTHONUNBUFFERED=1
export GOOGLE_APPLICATION_CREDENTIALS
export OCR_POST_CORRECTION
export EMAIL_HOST_PASSWORD
nohup python -u manage.py runserver 0.0.0.0:8088 --verbosity 2 &> log.runserver_8088 &
nohup redis-server redis.conf &> log.redis-server &
sleep 1

NUM_JOBS=3
for n in $(seq 1 $NUM_JOBS); do
    nohup python -u manage.py rqworker default &> log.rqworker_default_${n} &
done
