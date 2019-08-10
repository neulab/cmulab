# CMULAB ELAN Client

A simple client to add annotations to all the ELAN files in a directory.

## Preparation

First, install CMULAB overall by following the install instructions in the parent directory. Then install the requirements for the client from this directory

    pip install -r requirements.txt

## Annotation

Given a directory of ELAN files, parse them and get additional annotations from `model_name` to be stored in `output_tier`.

    python cmulab_elan.py --input_dir [dir] --input_tiers [tiers] --output_dir [dir] --output_tier [tier] --model_name [name]

## How to get annotations using the API

If you haven't already, set up a server by running the following
	
	  python manage.py makemigrations annotator
	  python manage.py migrate
	  python manage.py createsuperuser
	  python populate.py

The last one will create entries for the available models, including the VAD model that we will use.

With the server running (`python manage.py runserver` on another terminal), let's get annotations on the sample ELAN file.

	  python cmulab_elan.py --input_dir Chatino/ --output_dir output --output_tier VAD --model_name vad

This wil do the following:
	
* Create a test_corpus that will have a single AudioAnnotation, as parsed from the ELAN file. You can see the by navigating to `http://localhost:8000/annotator/corpus` 

* Obtain VAD annotations over the sample audio (it takes a while so we use a small audio sample of about ~2 seconds)

* Store the VAD annotations on the server's database. You can see the output by navigating to `http://localhost:8000/annotator/spantextannotation/` (Each `SpanTextAnnotation` corresponds to an active region)

* Produce a new ELAN file in the `output` dir, which includes the additional annotations.

Note that obtaining VAD annotations does not require reading in any tiers from the ELAN files, other than the wavfile.
If the annotation model requires additional input, you can provide the necessary tiers through the `--input_tiers` flag (e.g. `--input_tiers en` in our examples).

## Example Data (Chatino)

The two example .eaf and .wav files are in Eastern Chatino, taken from the Eastern Chatino (CTP) Speech Corpus
for GORILLA (http://gorilla.linguistlist.org/).

