#!/usr/bin/python
import argparse
import pympi
import glob
import sys
import os

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
# Needed for adding a model
from speech.models import Mlmodel
from speech.serializers import MlmodelSerializer
# Needed for adding a corpus
from speech.models import Corpus
from speech.serializers import CorpusSerializer
# Needed for adding segments
from speech.models import Segment
from speech.serializers import SegmentSerializer
# Needed for annotations
from speech.models import TextAnnotation
from speech.serializers import TextAnnotationSerializer
# Needed for span annotations
from speech.models import SpanTextAnnotation
from speech.serializers import SpanTextAnnotationSerializer


parser = argparse.ArgumentParser(
    description='Script retrieves schedules from a given server')
# Add arguments
parser.add_argument('--input_dir', type=str, default="/Users/antonis/research/cmulab/example-clients/Sib_01-f/", help='The directory full of elan files to input')
parser.add_argument('--input_tiers', default="Text", type=str, help='The tier or tiers to input (multiple tiers separated by comma. "media[ID]" is a special word that refers to the media file, where ID can optionally specify which ID for the media descriptor.)')
parser.add_argument('--output_dir', default="output", type=str, help='The directory to output to')
parser.add_argument('--output_tier', default="EDU", type=str, help='The output tier')
parser.add_argument('--model_name', default="vad", type=str, help='The model name to use')
parser.add_argument('--overwrite', action='store_true', help='Whether to overwrite existing files in the output directory')

#args = parser.parse_args()
args, unknown = parser.parse_known_args()
input_tiers = args.input_tiers.split(',')

if not os.path.isdir(args.output_dir):
  os.mkdir(args.output_dir)

def load_tier(elan, tier_name, input_dir):
  """
  Returns the data of a tier as a list of tuples:
    [ (start_time, end_time, annotation, id), ...]
    Note that the id field above is optional
  """
  if tier_name.startswith('media'):
    if tier_name == 'media':
      tier_id = 0
    else:
      tier_id = int(tier_name[5:])
    media_url = input_elan.media_descriptors[tier_id]['MEDIA_URL']
    relative_media_url = input_elan.media_descriptors[tier_id]['RELATIVE_MEDIA_URL']
    media_url_in_dir = os.path.join(input_dir, relative_media_url)
    base_url = os.path.basename(media_url)
    base_url_in_dir = os.path.join(input_dir, base_url)
    if os.path.isfile(media_url):
      use_url = media_url
    elif os.path.isfile(media_url_in_dir):
      use_url = media_url_in_dir
    elif os.path.isfile(base_url_in_dir):
      use_url = base_url_in_dir
    else:
      raise IOError(f'could not find media in either {media_url} or {media_url_in_dir}')
    with open(use_url, 'rb') as media_handle:
      media_data = media_handle.read()
    return ('media', media_data, input_elan.media_descriptors[tier_id]['MEDIA_URL'])
  else:
    try:
      tier_data = elan.get_annotation_data_for_tier(tier_name)
      return tier_data
    except KeyError:
      print(f"Didn't find tier {tier_name} in the elan file")
      return -1
    #raise NotImplementedError('Probably want to extract this and convert it into (annotation, start, end) notation')



def get_annotations(input_tier_data, input_tiers, model_name):
  """
  Read in data, send it to the server, and return the values
  
  Arguments:
    input_tier_data: The data to be sent to the server
    model_name: The model to use

  Returns:
    A list of tuples of annotations [(start, end, annot), (start, end, annot), ...]
  """
  factory = APIRequestFactory()
  request = factory.get('/')
  serializer_context = {'request': Request(request),}


  # Create a corpus with the input file
  corpus=Corpus(name="temp_corpus")
  corpus.save()

  # Create segments for each
  segments = [Segment(name=f"s{i}", corpus=corpus) for i,_ in enumerate(input_tier_data)]
  for s in segments:
    s.save()
  
  # Add the annotations:
  # First crate the audio annotation that stores the audio file for each segment
  # TODO(antonis): it is not currently possible to have the same audioannotation to multiple segments,
  #                 so that's why it has to be created many times
  audioannotations = [AudioAnnotation(audio_file_format='wav', audio="/Users/antonis/research/cmulab/example-clients/Sib_01-f/Sib_01-f.wav", segment=segments[i]) for i,_ in enumerate(input_tier_data)]
  for i,a in enumerate(audioannotations):
    audioannot.save()
  # The above is equivalent to running something like
  # (the audio annotation will have id=1 and we add it to all segments)
  # http -a antonis:password123 --json PUT http://localhost:8000/speech/segment/{i}/addannotations/{i}/
  # We would want instead a single audioannotation
  # http -a antonis:password123 --json PUT http://localhost:8000/speech/segment/{i}/addannotations/1/


  # Now the text annotations
  for j,input_tier in enumerate(input_tier_data_):
    for i,a in enumerate(input_tier):
      annot=SpanTextAnnotation(field_name=f"{input_tiers[j]}", segment=f"s{i}", text="a[2]", start=a[0], end=a[1], status=TextAnnotation.GENERATED)
      annot.save()
  # Now the database is populated
  

  # Get annotations with POST method
  # Run something equivalent to
  #    http -a antonis:password123 --json POST http://127.0.0.1:8000/annotator/model/<int:mk>/annotate/<int:sk>/
  # And retrieve the annotations with GET
  #    http -a antonis:password123 --json POST http://127.0.0.1:8000/annotator/segment/<int:sk>/annotations/
  return []
  raise NotImplementedError('need to implement get_annotations')


for input_file in glob.glob(f'{args.input_dir}/*.eaf'):
  print(input_file)
  basename = os.path.basename(input_file)
  output_file = os.path.join(args.output_dir, basename)
  if os.path.isfile(output_file) and not args.overwrite:
    print(f'WARNING: Skipping existing output file {output_file}', file=sys.stderr)
    continue
  
  input_elan = pympi.Elan.Eaf(file_path=input_file)

  try:
    #print(input_elan.tiers)
    print(input_elan.media_descriptors)
    print(input_elan.get_tier_names())
    #print(input_elan.timeslots)
    input_tier_data = [load_tier(input_elan, x, args.input_dir) for x in input_tiers]
    print(input_tier_data[0][:10])
    annotations = get_annotations(input_tier_data, input_tiers, args.model_name)
    input_elan.add_tier(args.output_tier)
    for val, start, end in annotations:
      input_elan.add_annotation(args.output_tier, start, end, value=val)
    input_elan.to_file(output_file)
  except IOError as e:
    print(f'WARNING: {e}')
