# CMULAB ELAN Client

A simple client to add annotations to all the ELAN files in a directory.

## Preparation

First, install CMULAB client API and other requirements

    pip install -r requirements.txt

## Annotation

Given a directory of ELAN files, parse them.

    python cmulab_elan.py input_directory input_tier output_directory output_tier model_name
