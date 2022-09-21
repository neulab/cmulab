#!/bin/bash

cd /
git clone https://github.com/shrutirij/ocr-post-correction
cd ocr-post-correction/
conda create --yes --name ocr-post-correction python=3.9.5
conda activate ocr-post-correction
pip install -r postcorr_requirements.txt
pip install -r ocr_requirements.txt
cp /cmulab/tests/cmulab_ocr_t*.sh .
cp /cmulab/tests/echo_cmulab_ocr_t*.sh .

conda create --yes --name cmulab python=3.7.10
conda activate cmulab
python setup.py develop
pip install git+https://github.com/zaidsheikh/cmulab_allosaurus
pip install git+https://github.com/zaidsheikh/cmulab_diarization
pip install git+https://github.com/zaidsheikh/cmulab_stanza
ln -s /dev/shm/.config/.env.yml .

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
