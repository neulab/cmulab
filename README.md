# CMU Linguistic Annotation Backend

Install the requirements and setup the environment for development
~~~~bash
bash ./setup.sh
~~~~

Create admin user and populate database with some initial data
~~~~
conda activate cmulab
python manage.py createsuperuser
python populate.py 
~~~~

CMULAB plugins (backend ML/NLP models) can be installed by simply running:
~~~~
python3 -m pip install git+https://github.com/zaidsheikh/cmulab_allosaurus
python3 -m pip install git+https://github.com/zaidsheikh/cmulab_diarization
...
~~~~

Optional steps to enable Google Sign-in:
- Create OAuth app at https://console.cloud.google.com/apis/credentials/oauthclient
- Login to http://localhost:8088/admin/socialaccount/socialapp and add social app

Start the server:

~~~~bash
bash ./start.sh
python manage.py createsuperuser
python populate.py 
~~~~

Docker image: [zs12/cmulab-devel](https://hub.docker.com/r/zs12/cmulab-devel/tags)

Live demo: https://cmulab.dev/
