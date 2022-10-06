import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmulab.settings')
import django
django.setup()

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.get('/')

serializer_context = {
    'request': Request(request),
}


# Add a couple of models
from annotator.models import Mlmodel
from annotator.serializers import MlmodelSerializer

model = Mlmodel(name="random_model_id", modelTrainingSpec="ocr-post-correction", status='ready', tags=Mlmodel.TRANSCRIPTION)
model.save()
