import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from django_filters.rest_framework import DjangoFilterBackend

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden

from rest_framework import generics
from rest_framework import status
from rest_framework import permissions

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from annotator.models import Mlmodel, Corpus, Segment
from annotator.models import Annotation, TextAnnotation, AudioAnnotation, SpanTextAnnotation

from annotator.permissions import IsOwnerOrReadOnly

from annotator.serializers import MlmodelSerializer, CorpusSerializer, SegmentSerializer, UserSerializer
from annotator.serializers import AnnotationSerializer, AudioAnnotationSerializer, TextAnnotationSerializer, SpanTextAnnotationSerializer

from annotator.BackendModels import MLModels
from annotator.models import Document, Transcript
from annotator.forms import DocumentForm

import django_rq
from allosaurus.model import get_all_models
from allosaurus.model import get_model_path
from allosaurus.lm.inventory import Inventory
import subprocess
import traceback
import json
import string, secrets
import glob
import pydub
import shutil
import tempfile
import datetime
import time
from pathlib import Path

import io
from contextlib import redirect_stdout, redirect_stderr


from django.core.files.storage import FileSystemStorage

from google.cloud import vision
from google.protobuf.json_format import MessageToJson
from pdf2image import convert_from_path
from django.views.decorators.csrf import csrf_exempt


import sys
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

backend_models = {}
for plugin in entry_points(group='cmulab.plugins'):
    backend_models[plugin.name] = plugin.load()

ocr_client = vision.ImageAnnotatorClient()
ocr_api_usage = {}

TEST_SINGLE_SOURCE_SCRIPT = os.environ.get(TEST_SINGLE_SOURCE_SCRIPT, "/ocr-post-correction/test_single-source.sh")
TRAIN_SINGLE_SOURCE_SCRIPT = os.environ.get(TRAIN_SINGLE_SOURCE_SCRIPT, "/ocr-post-correction/train_single-source.sh")


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'corpus': reverse('corpus-list', request=request, format=format),
        'model': reverse('model-list', request=request, format=format),
        'segment': reverse('segment-list', request=request, format=format),
        'annotation': reverse('annotation-list', request=request, format=format),
        'schema': reverse('schema', request=request, format=format),
    })


# Views for Corpora
class CorpusList(APIView):
        """
        List all corpora, or create a new corpus.
        """
        # This makes sure that only authenticated requests get served
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

        def get(self, request, format=None):
                corpus = Corpus.objects.all()
                serializer = CorpusSerializer(corpus, many=True)
                return Response(serializer.data)

        def post(self, request, format=None):
                serializer = CorpusSerializer(data=request.data)
                if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        # This ties the corpus to its owner (User)
        def perform_create(self, serializer):
                serializer.save(owner=self.request.user)


class CorpusDetail(APIView):
        """
        Retrieve, update or delete a corpus.
        """
        # This makes sure that only authenticated requests get served
        # and that only the Owner of a corpus can modify it
        permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

        def get_object(self, pk):
                try:
                        return Corpus.objects.get(pk=pk)
                except Corpus.DoesNotExist:
                        raise Http404

        def get(self, request, pk):
                corpus = self.get_object(pk)
                serializer = CorpusSerializer(corpus)
                return Response(serializer.data)

        def put(self, request, pk):
                corpus = self.get_object(pk)
                serializer = CorpusSerializer(corpus, data=request.data)
                if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, pk):
                corpus = self.get_object(pk)
                corpus.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)


class SegmentsInCorpus(APIView):
        """
        Retrieve the segments of a corpus.
        """
        # This makes sure that only authenticated requests get served
        # and that only the Owner of a corpus can modify it
        permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

        def get_object(self, pk):
                try:
                        return Corpus.objects.get(pk=pk)
                except Corpus.DoesNotExist:
                        raise Http404

        def get(self, request, pk, format=None):
                corpus = self.get_object(pk)
                segment = Segment.objects.filter(corpus=corpus.id)
                serializer = SegmentSerializer(segment, many=True)
                return Response(serializer.data)

@login_required(login_url='/annotator/login/')
@api_view(['GET', 'PUT'])
def addsegmentstocorpus(request, pk, s_list):
        try:
                corpus = Corpus.objects.get(pk=pk)
        except Corpus.DoesNotExist:
                raise Http404

        if request.method == 'GET':
                segment = Segment.objects.filter(corpus=corpus.id)
                serializer = SegmentSerializer(segment)
                return Response(serializer.data)

        elif request.method == 'PUT':
                segment_list = []
                segment_ids = s_list
                segment_ids = segment_ids.split(',')
                for s_id in segment_ids:
                        try:
                                segment = Segment.objects.get(pk=s_id)
                        except Segment.DoesNotExist:
                                raise Http404
                        segment.corpus=corpus
                        segment.name = segment.name
                        segment.save()
                        segment_list.append(segment)

                        serializer = SegmentSerializer(segment, data=request.data)
                        if not serializer.is_valid():
                                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        serializer.save()
                return Response(status=status.HTTP_202_ACCEPTED)

@login_required(login_url='/annotator/login/')
@api_view(['GET', 'PUT'])
def removesegmentsfromcorpus(request, pk, s_list):
        try:
                corpus = Corpus.objects.get(pk=pk)
        except Corpus.DoesNotExist:
                raise Http404

        if request.method == 'GET':
                segment = Segment.objects.filter(corpus=corpus.id)
                serializer = SegmentSerializer(segment)
                return Response(serializer.data)

        elif request.method == 'PUT':
                segment_list = []
                segment_ids = s_list
                segment_ids = segment_ids.split(',')
                try:
                        for s_id in segment_ids:
                                try:
                                        segment = Segment.objects.get(pk=s_id)
                                except Segment.DoesNotExist:
                                        raise Http404
                                segment.corpus=None
                                segment.save()
                                segment_list.append(segment)
                        return Response(status=status.HTTP_202_ACCEPTED)
                except:
                        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@login_required(login_url='/annotator/login/')
@api_view(['POST'])
def trainModel(request, pk):
        try:
                mlmodel = Mlmodel.objects.get(pk=pk)
        except Mlmodel.DoesNotExist:
                raise Http404

        if request.method == 'POST':
                return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


def subprocess_call():
        subprocess.run(['sleep', '5'])

def dummy_python_job(msg):
        print("Starting dummy python job")
        time.sleep(1)
        print("PROGRESS: 10%")
        time.sleep(1)
        print("PROGRESS: 20%")
        time.sleep(1)
        print("PROGRESS: 30%")
        time.sleep(1)
        print("PROGRESS: 40%")
        time.sleep(1)
        print("PROGRESS: 50%")
        sys.stderr.write("WARNING: test stderr message")
        time.sleep(1)
        return("SUCCESS: " + msg)



def batch_finetune_allosaurus(data_dir, log_file, pretrained_model, new_model_name, params, owner):
        print("Starting allosaurus fine-tuning job " + new_model_name)
        print("User: " + str(owner))
        print("User python type: " + str(type(owner)))
        tb = ""
        fs = FileSystemStorage()
        with fs.open(log_file, 'w') as f_stdout:
                with redirect_stderr(f_stdout):
                        with redirect_stdout(f_stdout):
                                try:
                                        model1 = Mlmodel(name=new_model_name, modelTrainingSpec="allosaurus", status=Mlmodel.TRAIN, tags=Mlmodel.TRANSCRIPTION)
                                        if not owner.is_anonymous:
                                                model1.owner = owner
                                        model1.save()
                                        print("New model ID: " + new_model_name)
                                        print(json.dumps(params, indent=4))
                                        print("Fine-tuning Allosaurus...")
                                        allosaurus_finetune = backend_models["allosaurus_finetune"]
                                        allosaurus_finetune(data_dir, pretrained_model, new_model_name, params)
                                except:
                                        tb = traceback.format_exc()
                                        print(tb)
        with fs.open(log_file, 'r') as f_stdout:
                str_stdout = f_stdout.read()
        allosaurus_models = [model.name for model in get_all_models()]
        # TODO: ask user if we should delete this or keep
        if os.path.exists(data_dir):
                shutil.rmtree(data_dir)
        if not tb and new_model_name in allosaurus_models:
                model1.status=Mlmodel.READY
                model1.save()
                msg = str_stdout + "\nTraining successful! New model name: " + new_model_name
                print(msg)
                return msg
        else:
                model1.status=Mlmodel.UNAVAILABLE
                model1.save()
                msg = str_stdout + "\nTraining failed for model " + new_model_name
                print(msg)
                return msg


# @login_required(login_url='/annotator/login/')
@api_view(['GET', 'PUT', 'POST'])
def annotate(request, mk, sk):
        #mk is the model id
        #sk is the segment id   
        segment = None
        try:
                segment = Segment.objects.get(pk=sk)
        except Segment.DoesNotExist:
                print("segment ID does not exist: " + str(sk))
                # raise Http404

        model = None
        try:
                model = Mlmodel.objects.get(pk=mk)
        except Mlmodel.DoesNotExist:
                print("model ID does not exist: " + str(mk))
                # raise Http404

        if request.method == 'GET':
                django_rq.enqueue(dummy_python_job, "test message!")
                # annot = Annotation.objects.filter(segment=segment.id)
                # serializer = AnnotationSerializer(annot)
                # return Response(serializer.data)
                return Response(status=status.HTTP_202_ACCEPTED)

        elif request.method == 'PUT':
                try:
                        # First retrieve the model details
                        modeltag = model.tags if model else ""
                        #audio_file_path = segment.
                        # Create a new annotation
                        if modeltag == 'vad':
                                # This is hard-coded, it probably shouldn't
                                act_model = MLModels.KhanagaModel()
                                # Need to get the annotation of the segment that is its audio file
                                # This is in the audioannotation.audio that corresponds to this segment
                                # TODO: Get the audio annotation that corresponds to this segment or fail
                                # audio_file_path = ...
                                audio_file_path = "/Users/antonis/research/cmulab/example-clients/Sib_01-f/Sib_01-f.wav"
                                act_model.get_results(audio_file_path)
                                #Crate a text annotation with the model's output
                                annot=TextAnnotation(field_name="vad", text=act_model.output, segment=segment, status=TextAnnotation.GENERATED)
                                annot.save()
                                return Response(status=status.HTTP_202_ACCEPTED)
                except Exception as e:
                        print(e)
                        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif request.method == 'POST':
                try:
                        # modeltag = model.tags
                        params = json.loads(request.POST.get("params", '{}'))
                        if params.get("service") == "diarization":
                                params = json.loads(request.POST.get("params", '{}'))
                                threshold = params.get("threshold", 0.45)
                                annotations = json.loads(request.POST.get("segments", "[]"))
                                segments, speakers = [], []
                                for annotation in annotations:
                                        speakers.append(annotation["value"].strip())
                                        segments.append([float(annotation["start"]), float(annotation["end"])])
                                fs = FileSystemStorage()
                                for audio_file in request.FILES.getlist('file'):
                                        filename = fs.save(audio_file.name, audio_file)
                                        uploaded_file_path = fs.path(filename)
                                        print('absolute file path', uploaded_file_path)
                                        diarization_model = backend_models["diarization"]
                                        response_data = diarization_model(str(uploaded_file_path), segments, speakers)
                                        fs.delete(filename)
                                return Response(response_data, status=status.HTTP_202_ACCEPTED)

                        # if modeltag == 'transcription' or modeltag == "allosaurus":
                        # if "pretrained_model" not in params:
                        if params.get("service") == "phone_transcription":
                                segments = json.loads(request.POST.get("segments", "[]"))
                                params = json.loads(request.POST.get("params", '{"lang": "eng"}'))
                                print(json.dumps(segments))
                                print(json.dumps(params))
                                if len(params["lang"].strip().split()) > 1:
                                    # this is actually a list of phones, write them to a file and pass to allosaurus
                                    # TODO: delete this
                                    phoneslist = tempfile.NamedTemporaryFile(suffix = '.txt', delete=False)
                                    phoneslist.close()
                                    Path(phoneslist.name).write_text('\n'.join(params["lang"].split()))
                                    params["lang"] = phoneslist.name
                                    print(params["lang"])
                                # TODO fixme: do not hardcode
                                # trans_model = MLModels.TranscriptionModel()
                                trans_model = backend_models["allosaurus"]
                                # audio_file = '/home/user/Downloads/delete/DSTA-project/ELAN_6-1/lib/app/extensions/allosaurus-elan/test/allosaurus.wav'
                                # audio_file = request.FILES['file']
                                fs = FileSystemStorage()
                                tmp_dir = tempfile.mkdtemp(prefix="allosaurus-elan-")
                                for audio_file in request.FILES.getlist('file'):
                                        filename = fs.save(audio_file.name, audio_file)
                                        uploaded_file_path = fs.path(filename)
                                        print('absolute file path', uploaded_file_path)
                                        if not uploaded_file_path.endswith('.wav'):
                                                converted_audio_file = tempfile.NamedTemporaryFile(suffix = '.wav')
                                                ffmpeg = shutil.which('ffmpeg')
                                                if ffmpeg:
                                                        subprocess.call([ffmpeg, '-y', '-v', '0', '-i', uploaded_file_path,'-ac', '1', '-ar', '16000', '-sample_fmt', 's16', '-acodec', 'pcm_s16le', converted_audio_file.name])
                                                else:
                                                        return Response("only WAV files are supported!", status=status.HTTP_400_BAD_REQUEST)
                                        else:
                                                converted_audio_file = open(uploaded_file_path, mode='rb')
                                        converted_audio = pydub.AudioSegment.from_file(converted_audio_file, format = 'wav')
                                        response_data = []
                                        if not segments:
                                                segments = [{'start': 0, 'end': len(converted_audio), 'value': ""}]
                                        for annotation in segments:
                                                annotation['clip'] = tempfile.NamedTemporaryFile(suffix = '.wav', dir = tmp_dir, delete=False)
                                                clip = converted_audio[annotation['start']:annotation['end']]
                                                clip.export(annotation['clip'], format = 'wav')
                                                print(annotation['clip'].name)
                                                # trans_model.get_results(annotation['clip'].name)
                                                trans_model_output = trans_model(annotation['clip'].name, params=params)
                                                response_data.append({
                                                        "start": annotation['start'],
                                                        "end": annotation['end'],
                                                        "transcription": trans_model_output
                                                })
                                        fs.delete(filename)
                                        if os.path.exists(converted_audio_file.name):
                                                os.remove(converted_audio_file.name)
                                if os.path.exists(tmp_dir):
                                        shutil.rmtree(tmp_dir)
                                return Response(response_data, status=status.HTTP_202_ACCEPTED)
                        # elif modeltag == "other" and model.name == "allosaurus_finetune":
                        elif "pretrained_model" in params:
                                print("finetuning...")
                                default_params = '{"lang": "eng", "epoch": 2, "pretrained_model": "uni2005"}'
                                params = json.loads(request.POST.get("params", default_params))
                                fs = FileSystemStorage()
                                tmp_dir = tempfile.mkdtemp(prefix="allosaurus-elan-")
                                if params.get("service") == "batch_finetune":
                                        for zip_file in request.FILES.getlist('file'):
                                                tmp_dir2 = tempfile.mkdtemp(prefix="allosaurus-elan-")
                                                # TODO: remove files afterwards
                                                filename = fs.save(zip_file.name, zip_file)
                                                uploaded_file_path = fs.path(filename)
                                                print('absolute file path', uploaded_file_path)
                                                print('temp dir', tmp_dir)
                                                print('temp dir 2', tmp_dir2)
                                                shutil.unpack_archive(uploaded_file_path, tmp_dir)
                                                train_dir_path = Path(tmp_dir2) / "train"
                                                validate_dir_path = Path(tmp_dir2) / "validate"
                                                train_dir_path.mkdir(parents=True, exist_ok=True)
                                                for wav_file in glob.glob(tmp_dir + "/train/*.wav"):
                                                        full_audio = pydub.AudioSegment.from_file(wav_file, format = 'wav')
                                                        json_file = os.path.splitext(wav_file)[0] + ".json"
                                                        with open(json_file, 'r') as fjson:
                                                                transcriptions = json.load(fjson)
                                                        for start_end in transcriptions:
                                                                start, end = map(int, start_end.split('-'))
                                                                transcription = transcriptions[start_end][0]
                                                                segment_id = os.path.basename(os.path.splitext(wav_file)[0]) + '_' + start_end
                                                                clip = full_audio[start:end]
                                                                clip.export(train_dir_path / (segment_id + ".wav"), format = 'wav')
                                                                (train_dir_path / (segment_id + ".txt")).write_text(transcription)
                                                shutil.copytree(train_dir_path.resolve(), validate_dir_path.resolve())
                                                allosaurus_finetune = backend_models["allosaurus_finetune"]
                                                pretrained_model = params.get("pretrained_model", "uni2005")
                                                # new_model_id = pretrained_model + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                                                suffix = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(8))
                                                new_model_id = '_'.join([pretrained_model, params["lang"], suffix])
                                                # allosaurus_finetune(tmp_dir2, pretrained_model, new_model_id, params)
                                                job_id = "allosaurus_finetune_"+new_model_id
                                                auth_token = request.META.get('HTTP_AUTHORIZATION', '').strip()
                                                if auth_token:
                                                        try:
                                                                print("Auth token: " + auth_token)
                                                                request.user = Token.objects.get(key=auth_token).user
                                                                print("Username: " + request.user.get_username())
                                                        except:
                                                                return Response(status=status.HTTP_401_UNAUTHORIZED)
                                                else:
                                                        return Response(status=status.HTTP_401_UNAUTHORIZED)
                                                print("User: " + str(request.user))
                                                print("User python type: " + str(type(request.user)))
                                                log_file = "allosaurus_finetune_" + new_model_id + "_log.txt"
                                                job = django_rq.enqueue(batch_finetune_allosaurus, tmp_dir2, log_file, pretrained_model, new_model_id, params, request.user,
                                                                        job_id=job_id, result_ttl=-1)
                                                print('fine-tuned model ID', new_model_id)
                                                print('RQ job ID', job_id)
                                                fs.delete(filename)
                                        if os.path.exists(tmp_dir):
                                                shutil.rmtree(tmp_dir)
                                        return Response([{"new_model_id": new_model_id,
                                                "job_id": job_id,
                                                "status_url": "/annotator/media/" + log_file,
                                                "models_url": request.build_absolute_uri("/annotator/upload/#models"),
                                                "lang": params["lang"],
                                                "status": job.get_status()}], status=status.HTTP_202_ACCEPTED)
                                else:
                                        # old version of fine-tuning service, no longer used TODO: DELETE THIS
                                        for zip_file in request.FILES.getlist('file'):
                                                filename = fs.save(zip_file.name, zip_file)
                                                uploaded_file_path = fs.path(filename)
                                                print('absolute file path', uploaded_file_path)
                                                print('temp dir', tmp_dir)
                                                shutil.unpack_archive(uploaded_file_path, tmp_dir)
                                                allosaurus_finetune = backend_models["allosaurus_finetune"]
                                                pretrained_model = params.get("pretrained_model", "eng2102")
                                                new_model_id = pretrained_model + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                                                print('fine-tuned model ID', new_model_id)
                                                allosaurus_finetune(tmp_dir, pretrained_model, new_model_id, params)
                                                fs.delete(filename)
                                        if os.path.exists(tmp_dir):
                                                shutil.rmtree(tmp_dir)
                                        return Response([{"new_model_id": new_model_id, "lang": params["lang"], "status": "success"}], status=status.HTTP_202_ACCEPTED)
                except Exception as e:
                        # traceback.print_exc()
                        error_msg = ''.join(traceback.format_exc())
                        print(error_msg)
                        return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required(login_url='')
def list_models(request):
    return redirect(reverse('home') + '#models')


@login_required(login_url='')
def list_home(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.owner = request.user
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('list_home'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.filter(owner=request.user)
    ml_models = Mlmodel.objects.filter(owner=request.user).reverse()


    # Render list page with the documents and the form
    return render(request, 'list.html', {'documents': documents, 'ml_models': ml_models, 'form': form})

def ocr_frontend(request):
    # TODO: fix this, no longer works (ocr_frontend.html used to be symlink to index.html)
    return render(request, "ocr_frontend.html", {})

@api_view(['POST'])
@csrf_exempt
def ocr_post_correction(request):
    global ocr_client, ocr_api_usage
    auth_token = request.META.get('HTTP_AUTHORIZATION', '').strip()
    if auth_token:
        try:
            request.user = Token.objects.get(key=auth_token).user
            username = request.user.get_username()
        except:
            return HttpResponse("Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse("Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        params = json.loads(request.POST.get("params", "{}"))
        fs = FileSystemStorage()
        text = {}
        images = []
        for uploaded_file in request.FILES.getlist('file'):
            if params.get("store_files", False):
                # TODO: save these files (along with transcripts)
                newdoc = Document(docfile = uploaded_file)
                newdoc.owner = request.user
                newdoc.save()
            filename = fs.save(uploaded_file.name, uploaded_file)
            filepath = fs.path(filename)
            if uploaded_file.name.endswith('.pdf'):
                tmp_dir = tempfile.mkdtemp(prefix="pdf2image_")
                images += convert_from_path(filepath, dpi=400, paths_only=True, fmt='png', output_folder=tmp_dir)
            else:
                images.append(filepath)
        # TODO: retrieve images/transcripts from db
        # documents = Document.objects.filter(owner=request.user)
        for filepath in images:
            print(filepath)
            print(f"{username} OCR API usage: {ocr_api_usage.get(username, 0)}")
            print(ocr_api_usage)
            # TODO: write a better rate-limiting system
            if ocr_api_usage.get(username, 0) > 100:
                return HttpResponseForbidden()
            ocr_api_usage[username] = ocr_api_usage.get(username, 0) + 1
            with io.open(filepath, "rb") as image_file:
                content = image_file.read()
                image = vision.Image(content=content)
                if params.get("debug", False):
                    response_text = "Sample text"
                else:
                    response = ocr_client.document_text_detection(image=image)
                    response_text = response.full_text_annotation.text
                    if params.get("store_files", False):
                        # TODO: store these transcripts in the db
                        newdoc = Transcript(filename = os.path.basename(image_file.name), text = response_text)
                        newdoc.owner = request.user
                        newdoc.save()
                text[os.path.basename(image_file.name)] = response_text
        return Response(text, status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
@csrf_exempt
def test_single_source_ocr(request):
    params = {}
    job = django_rq.enqueue(test_single_source_ocr_job, tmp_dir, log_file, pretrained_model, params, request.user)

def test_single_source_ocr_job(wdir, logfile, model, params, user):
    rc = subprocess.call(TEST_SINGLE_SOURCE_SCRIPT, shell=True)

@api_view(['POST'])
@csrf_exempt
def train_single_source_ocr(request):
    params = {}
    job = django_rq.enqueue(train_single_source_ocr_job, tmp_dir, log_file, pretrained_model, params, request.user)

def train_single_source_ocr_job(wdir, logfile, model, params, user):
    rc = subprocess.call(TRAIN_SINGLE_SOURCE_SCRIPT, shell=True)

@login_required(login_url='')
def get_auth_token(request):
    token, created = Token.objects.get_or_create(user=request.user)
    return HttpResponse(token.key)


def get_allosaurus_models(request):
    result = []
    # models = get_all_models()
    # TODO: fixme
    for model in ["eng2102", "uni2005"]:
        model_path = get_model_path(model)
        inventory = Inventory(model_path)
        result.append((model, [("ipa", f"Entire {model} phone inventory")] + sorted(zip(inventory.lang_ids, inventory.lang_names))))
        # for lang_id in inventory.lang_ids:
            # mask = inventory.get_mask(lang_id)
            # unit = mask.target_unit
            # phones = ' '.join(list(unit.id_to_unit.values())
    return render(request, 'allosaurus_models.html', {'result': result})


def get_allosaurus_phones(request, model_name, lang_id):
    model_path = get_model_path(model_name)
    inventory = Inventory(model_path)
    mask = inventory.get_mask(lang_id)
    unit = mask.target_unit
    phones = '<br>'.join(list(unit.id_to_unit.values()))
    return HttpResponse(phones)


def check_auth_token(request):
    auth_token = request.META.get('HTTP_AUTHORIZATION', '').strip()
    if auth_token:
        try:
            request.user = Token.objects.get(key=auth_token).user
        except:
            return HttpResponse("Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        return HttpResponse("Authorized")
    else:
        return HttpResponse("Unauthorized", status=status.HTTP_401_UNAUTHORIZED)


class AnnotationsInSegment(APIView):
        """
        Retrieve the annotations of a specific segment.
        """
        # This makes sure that only authenticated requests get served
        # and that only the Owner of a corpus can modify it
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

        def get_object(self, pk):
                try:
                        return Segment.objects.get(pk=pk)
                except Segment.DoesNotExist:
                        raise Http404

        def get(self, request, pk, format=None):
                segment = self.get_object(pk)
                annot = Annotation.objects.filter(segment=segment.id)
                serializer = AnnotationSerializer(annot, many=True)
                return Response(serializer.data)


@login_required(login_url='/annotator/login/')
@api_view(['GET', 'PUT'])
def addannotationstosegment(request, pk, s_list):
        try:
                segment = Segment.objects.get(pk=pk)
        except Segment.DoesNotExist:
                raise Http404

        if request.method == 'GET':
                annot = Annotation.objects.filter(segment=segment.id)
                serializer = AnnotationSerializer(annot)
                return Response(serializer.data)

        elif request.method == 'PUT':
                annot_list = []
                annot_ids = s_list
                annot_ids = annot_ids.split(',')
                for a_id in annot_ids:
                        try:
                                annot = Annotation.objects.get(pk=a_id)
                        except Annotation.DoesNotExist:
                                raise Http404
                        annot.segment=segment
                        annot.field_name = annot.field_name
                        annot.status = annot.status
                        # TODO: add subclass specific fields
                        annot.save()
                        annot_list.append(annot)

                        serializer = AnnotationSerializer(annot, data=request.data)
                        if not serializer.is_valid():
                                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        serializer.save()
                return Response(status=status.HTTP_202_ACCEPTED)

@login_required(login_url='/annotator/login/')
@api_view(['GET', 'PUT'])
def removeannotationsfromsegment(request, pk, s_list):
        try:
                segment = Segment.objects.get(pk=pk)
        except Segment.DoesNotExist:
                raise Http404

        if request.method == 'GET':
                annot = Annotation.objects.filter(segment=segment.id)
                serializer = AnnotationSerializer(segment)
                return Response(serializer.data)

        elif request.method == 'PUT':
                annot_list = []
                annot_ids = s_list
                annot_ids = annot_ids.split(',')
                try:
                        for a_id in annot_ids:
                                try:
                                        annot = Annotation.objects.get(pk=a_id)
                                except Annotation.DoesNotExist:
                                        raise Http404
                                annot.segment=None
                                annot.save()
                                annot_list.append(annot)
                        return Response(status=status.HTTP_202_ACCEPTED)
                except:
                        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# These generic API views for annotations work too
class SegmentList(generics.ListCreateAPIView):
        """
        List all segments, or create a new segment
        """
        queryset = Segment.objects.all()
        serializer_class = SegmentSerializer
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        filter_backends = (DjangoFilterBackend,)
        filterset_fields = ('corpus',)
        # This ties the corpus to its owner (User)
        #def perform_create(self, serializer):
        #       serializer.save(owner=self.request.user)

class SegmentDetail(generics.RetrieveUpdateAPIView):
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        queryset = Segment.objects.all()
        serializer_class = SegmentSerializer



# These generic API views for annotations work too
class ModelList(generics.ListCreateAPIView):
        queryset = Mlmodel.objects.all()
        serializer_class = MlmodelSerializer
        filter_backends = (DjangoFilterBackend,)
        filterset_fields = ('status', 'tags',)

# class ModelDetail(generics.RetrieveUpdateAPIView):
        # queryset = Mlmodel.objects.all()
        # serializer_class = MlmodelSerializer

class ModelDetail(generics.RetrieveUpdateDestroyAPIView):
        queryset = Mlmodel.objects.all()
        serializer_class = MlmodelSerializer


class AnnotationList(generics.ListCreateAPIView):
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        queryset = Annotation.objects.all()
        serializer_class = AnnotationSerializer
        filter_backends = (DjangoFilterBackend,)
        filterset_fields = ('status', 'segment',)

class AnnotationDetail(generics.RetrieveUpdateAPIView):
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        queryset = Annotation.objects.all()
        serializer_class = AnnotationSerializer

class AudioAnnotationList(generics.ListCreateAPIView):
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        queryset = AudioAnnotation.objects.all()
        serializer_class = AudioAnnotationSerializer
        filter_backends = (DjangoFilterBackend,)
        filterset_fields = ('status', 'segment', )

class AudioAnnotationDetail(generics.RetrieveUpdateAPIView):
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        queryset = AudioAnnotation.objects.all()
        serializer_class = AudioAnnotationSerializer

class TextAnnotationList(generics.ListCreateAPIView):
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        queryset = TextAnnotation.objects.all()
        serializer_class = TextAnnotationSerializer
        filter_backends = (DjangoFilterBackend,)
        filterset_fields = ('status', 'segment',)

class TextAnnotationDetail(generics.RetrieveUpdateAPIView):
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        queryset = TextAnnotation.objects.all()
        serializer_class = TextAnnotationSerializer

class SpanTextAnnotationList(generics.ListCreateAPIView):
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        queryset = SpanTextAnnotation.objects.all()
        serializer_class = SpanTextAnnotationSerializer
        filter_backends = (DjangoFilterBackend,)
        filterset_fields = ('status', 'segment',)

class SpanTextAnnotationDetail(generics.RetrieveUpdateAPIView):
        permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
        queryset = SpanTextAnnotation.objects.all()
        serializer_class = SpanTextAnnotationSerializer



# Generic API views
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

