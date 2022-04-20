#!/bin/bash


conda create --yes --name cmulab python=3.7.10
conda activate cmulab
python setup.py develop
pip install git+https://github.com/zaidsheikh/cmulab_allosaurus
pip install git+https://github.com/zaidsheikh/cmulab_diarization
pip install git+https://github.com/zaidsheikh/cmulab_stanza

python manage.py makemigrations annotator
python manage.py migrate

## Run the following manually:
# export PYTHONUNBUFFERED=1
# nohup python -u manage.py runserver 0.0.0.0:8088 --verbosity 2 &
# python manage.py createsuperuser
# python populate.py 
# nohup redis-server redis.conf &> log.redis-server &
# nohup python -u manage.py rqworker default &> log.rqworker_default &
# Create OAuth app at https://console.cloud.google.com/apis/credentials/oauthclient
# Login to http://localhost:8088/admin/socialaccount/socialapp and add social app
