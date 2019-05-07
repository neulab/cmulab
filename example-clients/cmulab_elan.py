import argparse
import pympi
import glob
import sys
import os

parser = argparse.ArgumentParser(
    description='Script retrieves schedules from a given server')
# Add arguments
parser.add_argument('input_dir', type=str, help='The directory full of elan files to input')
parser.add_argument('input_tiers', type=str, help='The tier or tiers to input (multiple tiers separated by comma. "media[ID]" is a special word that refers to the media file, where ID can optionally specify which ID for the media descriptor.)')
parser.add_argument('output_dir', type=str, help='The directory to output to')
parser.add_argument('output_tier', type=str, help='The directory to output to')
parser.add_argument('model_name', type=str, help='The model name to use')
parser.add_argument('--overwrite', action='store_true', help='Whether to overwrite existing files in the output directory')

args = parser.parse_args()
input_tiers = args.input_tiers.split(',')

if not os.path.isdir(args.output_dir):
  os.mkdir(args.output_dir)

def load_tier(elan, tier_name, input_dir):
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
    raise NotImplementedError('Probably want to extract this and convert it into (annotation, start, end) notation')

def get_annotations(input_tier_data, model_name):
  """
  Read in data, send it to the server, and return the values
  
  Arguments:
    input_tier_data: The data to be sent to the server
    model_name: The model to use

  Returns:
    A list of tuples of annotations [(annot, start, end), (annot, start, end), ...]
  """
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
    print(input_elan.tiers)
    input_tier_data = [load_tier(input_elan, x, args.input_dir) for x in input_tiers]
    annotations = get_annotations(tier_data, model_name)
    input_elan.add_tier(args.output_tier)
    for val, start, end in annotations:
      input_elan.add_annotation(args.output_tier, start, end, value=val)
    input_elan.to_file(output_file)
  except IOError as e:
    print(f'WARNING: {e}')
