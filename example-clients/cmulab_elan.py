#!/usr/bin/python
import argparse
import pympi
import glob
import sys
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmulab.settings')
import django
django.setup()


from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

# Needed for adding a model
from annotator.models import Mlmodel
from annotator.serializers import MlmodelSerializer
# Needed for adding a corpus
from annotator.models import Corpus
from annotator.serializers import CorpusSerializer
# Needed for adding segments
from annotator.models import Segment
from annotator.serializers import SegmentSerializer
# Needed for annotations
from annotator.models import TextAnnotation
from annotator.serializers import TextAnnotationSerializer
# Needed for span annotations
from annotator.models import SpanTextAnnotation
from annotator.serializers import SpanTextAnnotationSerializer
# Needed for audio annotations
from annotator.models import AudioAnnotation
from annotator.serializers import AudioAnnotationSerializer
# Load the backend models
from annotator.BackendModels import MLModels


parser = argparse.ArgumentParser(description='Script retrieves schedules from a given server')
# Add arguments
parser.add_argument('--input_dir', type=str, default="/Users/antonis/research/cmulab/example-clients/Sib_01-f/", help='The directory full of elan files to input')
parser.add_argument('--input_tiers', type=str, help='The tier or tiers to input (multiple tiers separated by comma. "media[ID]" is a special word that refers to the media file, where ID can optionally specify which ID for the media descriptor.)')
parser.add_argument('--output_dir', default="output", type=str, help='The directory to output to')
parser.add_argument('--output_tier', default="vad", type=str, help='The output tier')
parser.add_argument('--model_name', default="vad", choices=['vad', 'transcription', 'phoneseg'], type=str, help='The model name to use')
parser.add_argument('--overwrite', action='store_true', help='Whether to overwrite existing files in the output directory')

#args = parser.parse_args()
args, unknown = parser.parse_known_args()
if args.input_tiers:
  input_tiers = args.input_tiers.split(',')
else:
  input_tiers = [""]


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
      if tier_name:
        print(f"Didn't find tier {tier_name} in the elan file")
      return -1
    #raise NotImplementedError('Probably want to extract this and convert it into (annotation, start, end) notation')



def get_annotations(input_tier_data, input_tiers, wavfile, corpus, segment_counter, model_name):
  """
  Read in data, send it to the server, and return the values
  
  Arguments:
    input_tier_data: Pointer to the parsed ELAN file 
    input_tiers: The tiers to be sent to the server
    wavfile: The path to the audio file
    corpus: The corpus that the segments will be added to
    model_name: The model to use

  Returns:
    A list of tuples of annotations [(start, end, annot), (start, end, annot), ...]
  """
  #factory = APIRequestFactory()
  #user = User.objects.get(username='antonis')
  #view = AccountDetail.as_view()
  #request = factory.get('/')
  #force_authenticate(request, user=user)
  #response = view(request)

  #serializer_context = {'request': Request(request),}

  # Create segments for each
  segments = [Segment(name=f"s{segment_counter}_{i+1}", corpus=corpus) for i,_ in enumerate(input_tier_data)]
  for s in segments:
    s.save()
  
  # Add the annotations:
  # First crate the audio annotation that stores the audio file for each segment
  # TODO(antonis): it is not currently possible to have the same audioannotation to multiple segments,
  #                 so that's why it has to be created many times
  audioannotations = [AudioAnnotation(field_name='audio', status='correct', audio_file_format='wav', audio="example-clients/Sib_01-f/Sib_01-f.wav", segment=segments[i]) for i,_ in enumerate(input_tier_data)]
  for i,a in enumerate(audioannotations):
    a.save()
  # The above is equivalent to running something like
  # (the audio annotation will have id=1 and we add it to all segments)
  # http -a antonis:password123 --json PUT http://localhost:8000/speech/segment/{i}/addannotations/{i}/
  # We would want instead a single audioannotation
  # http -a antonis:password123 --json PUT http://localhost:8000/speech/segment/{i}/addannotations/1/


  # Now the text annotations
  for j,input_tier in enumerate(input_tier_data):
    if input_tier != -1: # if the tier wasn't found in the elan file, it will be -1
      for i,a in enumerate(input_tier):
        annot=SpanTextAnnotation(field_name=f"{input_tiers[j]}", segment=segments[j], text=f"{a[2]}", start=a[0], end=a[1], status=TextAnnotation.GENERATED)
        annot.save()
  # Now the database is populated
  
  # This is the way to get all models
  # Mlmodel.objects.all()
  # This is the way to filter out only the models tagged as "vad" and pick the first one
  # vad_model = Mlmodel.objects.filter(tags="vad")[0]
  
  # Now we get the actual model as defined by the BackendModels.
  # vad_model.modelTrainingSpec should be equal to the one below
  if model_name == "vad":
    act_model = MLModels.VADModel()
    window=0.5 # half a second
    threshold = 0.3 # 33% of the signal's energy is used as a threshold
    act_model.get_results(wavfile, threshold, window)
    # Now the output of the model is in act_model.output
    # which is a list of dictionaries
    out = []
    for d in act_model.output:
      # Save the span text annotations
      vad_annot=SpanTextAnnotation(field_name="vad", start=d['speech_begin'], end=d['speech_end'], text="v", segment=segments[0], status=TextAnnotation.GENERATED)
      vad_annot.save()
      # This should be in milliseconds
      out.append((vad_annot.text, int(vad_annot.start*1000), int(vad_annot.end*1000)))
    # Return the spantext annotations
    return out
  elif model_name == "transcription":
    act_model = MLModels.TranscriptionModel()
    act_model.get_results(wavfile)
    # Now the output of the model is in act_model.output
    vad_annot=TextAnnotation(field_name="phones", text=act_model.output, segment=segments[0], status=TextAnnotation.GENERATED)
    vad_annot.save()
    # We return the span which is from 0 to the end of the last segment
    return [(vad_annot.text, 0, int(input_tier_data[0][-1][1]*1000))]
  elif model_name == "phoneseg":
    act_model = MLModels.KhanagaModel()
    act_model.get_results(wavfile)
    # Now the output of the model is in act_model.output
    vad_annot=TextAnnotation(field_name="phoneseg", text=act_model.output, segment=segments[0], status=TextAnnotation.GENERATED)
    vad_annot.save()
    # For VAD we return the span which is from 0 to the end of the last segment
    return [(vad_annot.text, 0, int(input_tier_data[0][-1][1]*1000))]
  

#First create a corpus to put all the segments
corpus=Corpus(name="test_corpus")
corpus.save()

segment_counter = 0

for input_file in glob.glob(f'{args.input_dir}/*.eaf'):
  print(input_file)
  basename = os.path.basename(input_file)
  output_file = os.path.join(args.output_dir, basename)
  if os.path.isfile(output_file) and not args.overwrite:
    print(f'WARNING: Skipping existing output file {output_file}', file=sys.stderr)
    continue
  
  input_elan = pympi.Elan.Eaf(file_path=input_file)

  try:
    segment_counter += 1
    print(f"ELAN Media descriptors: {input_elan.media_descriptors}")
    WAVFILE = os.path.join(args.input_dir, input_elan.media_descriptors[0]['RELATIVE_MEDIA_URL'])
    print(f"The wavefile for this segment is {WAVFILE}")
    print(f"ELAN Available Tier names: {input_elan.get_tier_names()}")
    input_tier_data = [load_tier(input_elan, x, args.input_dir) for x in input_tiers]
    
    annotations = get_annotations(input_tier_data, input_tiers, WAVFILE, corpus, segment_counter, args.model_name)
    input_elan.add_tier(args.output_tier)
    for val, start, end in annotations:
      input_elan.add_annotation(args.output_tier, start, end, value=val)
    # TODO(antonis): The following fails with my weird ELAN file
    # But the produced vad annotation is stored in the database
    input_elan.to_file(output_file)
    
  except IOError as e:
    print(f'WARNING: {e}')
    