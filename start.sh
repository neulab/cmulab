#!/bin/bash


source activate cmulab
set -x

pkill -f rqworker
pkill -f runserver
pkill -f redis-server

python manage.py makemigrations annotator
python manage.py migrate
export PYTHONUNBUFFERED=1
nohup python -u manage.py runserver 0.0.0.0:8088 --verbosity 2 &> log.runserver_8088 &
nohup redis-server redis.conf &> log.redis-server &
sleep 1
nohup python -u manage.py rqworker default &> log.rqworker_default &
