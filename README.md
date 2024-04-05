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

## Backend models

CMULAB offers two options for deploying backend ML/NLP models: as python-based plugins or as external servers that communicate with CMULAB through REST APIs.

### CMULAB plugins
You can add new features to CMULAB by implementing them as Python packages and [registering them as plugins](https://setuptools.pypa.io/en/latest/userguide/entry_point.html#dynamic-discovery-of-services-and-plugins) under the "cmulab.plugins" category during setup. CMULAB will manage the allocation of jobs to the appropiate task queues and spinning up background workers.

CMULAB's phoneme recognition (using Allosaurus, a pretrained universal phone recognizer) and speaker diarization (using a model based
on Resemblyzer) functionality is implemented using this method.

~~~~
conda activate cmulab
python3 -m pip install git+https://github.com/zaidsheikh/cmulab_allosaurus
python3 -m pip install git+https://github.com/zaidsheikh/cmulab_diarization
...
~~~~

### External REST APIs
Alternatively, new functionality can be integrated using external servers that communicate with CMULAB using REST APIs. An example is our [translation server](https://github.com/zaidsheikh/cog_translation_server) powered by NLLB.