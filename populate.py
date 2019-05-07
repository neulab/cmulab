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

model1=Mlmodel(name="VAD_model", modelTrainingSpec="python silence.py < {input} > {output}", status='ready', tags=Mlmodel.VAD)
model1.save()

model2=Mlmodel(name="transcription", modelTrainingSpec="require: pytorch; python transcribe.py < {input} {model} > {output}", status='ready', tags=Mlmodel.TRANSCRIPTION)
model2.save()

model3=Mlmodel(name="transcription2", modelTrainingSpec="require: dynet; python transcribe.py < {input} {model} > {output}", status='training', tags=Mlmodel.TRANSCRIPTION)
model3.save()


# Add some corpora

from annotator.models import Corpus
from annotator.serializers import CorpusSerializer

corpus1=Corpus(name="mboshi")
corpus1.save()

corpus2=Corpus(name="griko")
corpus2.save()


# Add some segments

from annotator.models import Segment
from annotator.serializers import SegmentSerializer

segment1=Segment(name="s1", corpus=corpus1)
segment1.save()

segment2=Segment(name="s2", corpus=corpus2)
segment2.save()

segment3=Segment(name="s3", corpus=corpus2)
segment3.save()

segment4=Segment(name="s4", corpus=corpus2)
segment4.save()


# Add annotations
from annotator.models import TextAnnotation
from annotator.serializers import TextAnnotationSerializer

annot=TextAnnotation(field_name="location", segment=segment2, text="Calimera", status=TextAnnotation.CORRECT)
annot.save()

annot=TextAnnotation(field_name="location", segment=segment3, text="Martano", status=TextAnnotation.CORRECT)
annot.save()


from annotator.models import SpanTextAnnotation
from annotator.serializers import SpanTextAnnotationSerializer

annot=SpanTextAnnotation(field_name="phonemes", segment=segment2, text="c", start=0.01, end=0.05, status=TextAnnotation.GENERATED)
annot.save()

annot=SpanTextAnnotation(field_name="phonemes", segment=segment2, text="c", start=0.05, end=0.12)
annot.save()

