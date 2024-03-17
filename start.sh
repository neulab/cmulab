#!/bin/bash


PORT=${1:-8088}

. /opt/conda/etc/profile.d/conda.sh
[[ $CONDA_DEFAULT_ENV == "base" ]] || eval $(command conda shell.bash hook)
conda activate cmulab 2>/dev/null
[[ $CONDA_DEFAULT_ENV == "cmulab" ]] || source activate cmulab
[[ $CONDA_DEFAULT_ENV == "cmulab" ]] || { echo "Couldn't activate conda env cmulab. Exiting!"; exit 1; }
echo "conda activate $CONDA_DEFAULT_ENV"

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

timestamp=$(date +"%Y%m%d%H%M%S")
mkdir -p logs/${timestamp}
mv logs/log.* logs/${timestamp}

nohup python -u manage.py runserver 0.0.0.0:${PORT} --verbosity 2 &> logs/log.runserver_${PORT} &
nohup redis-server redis.conf &> logs/log.redis-server &
sleep 5

NUM_JOBS=3
for n in $(seq 1 $NUM_JOBS); do
    nohup python -u manage.py rqworker default &> logs/log.rqworker_default_${n} &
done
