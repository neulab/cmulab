# CMULAB ELAN Client

A simple client to add annotations to all the ELAN files in a directory.

## Preparation

First, install CMULAB client API and other requirements

    pip install -r requirements.txt

## Annotation

Given a directory of ELAN files, parse them and get additional annotations from `model_name` to be stored in `output_tier`.

    python cmulab_elan.py input_directory input_tier output_directory output_tier model_name


## How to get annotations using the API

If you haven't already, set up a server by running the following
	
	python manage.py makemigrations annotator
	python manage.py migrate
	python manage.py createsuperuser
	python populate.py

The last one will create entries for the available models, including the VAD model that we will use.

With the server running (`python manage.py runserver` on another terminal), let's get annotations on the sample ELAN file.

	py cmulab_elan.py example-clients/Sib_01-f/ Text output EDU vad

This wil do the following:
	
	* Create a test_corpus that will have the audio and the `Text` SpanTextAnnotations, as parsed from the ELAN file. You can see the by navigating to `http://localhost:8000/annotator/corpus` 
	* Obtain VAD annotations over the sample audio (it takes a while so we use a small audio sample of about ~2 seconds)
	* Store the VAD annotation on the server's database. You can see the output by navigating to `http://localhost:8000/annotator/textannotation/` (this should be the only `TextAnnotation` in this case)

It should also produce an output ELAN file, but the sample that we started with doesn't play well  with pympi, it has an unknown ELAN spec, so it cannot be properly exported back.
