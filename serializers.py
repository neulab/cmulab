
from django.contrib.auth.models import User

from rest_framework import serializers

from annotator.models import Mlmodel, Corpus, Segment
from annotator.models import Annotation, TextAnnotation, AudioAnnotation, SpanTextAnnotation


#class MlmodelSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Mlmodel
#        fields = ('id', 'audio', 'title', 'vad', 'phone_boundaries', 'spectrum_path')

class MlmodelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mlmodel
        fields = ('id', 'name', 'created', 'modelTrainingSpec', 'status', 'tags')


class CorpusSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    #segments = serializers.HyperlinkedRelatedField( many=True, read_only=True, view_name='segment-detail')
    segment = serializers.PrimaryKeyRelatedField(many=True, queryset=Segment.objects.all())
    class Meta:
        model = Corpus
        fields = ('id', 'name', 'owner', 'segment')

class SegmentSerializer(serializers.HyperlinkedModelSerializer):
    #annotation = serializers.PrimaryKeyRelatedField(many=True, queryset=Annotation.objects.all())
    corpus = serializers.ReadOnlyField(source='corpus.id', allow_null=True)
    annotation = serializers.PrimaryKeyRelatedField(many=True, read_only=True, allow_null=True) #view_name='annotation-detail')
    #annotation = serializers.PrimaryKeyRelatedField(many=True, queryset=Annotation.objects.all()) #view_name='annotation-detail')
    class Meta:
        model = Segment
        fields = ('id', 'name', 'corpus', 'annotation')

class AnnotationSerializer(serializers.HyperlinkedModelSerializer):
    segment = serializers.ReadOnlyField(source='segment.id', allow_null=True)
    class Meta:
        model = Annotation
        fields = ('id', 'field_name', 'segment', 'status')

class AudioAnnotationSerializer(AnnotationSerializer):
    class Meta(AnnotationSerializer.Meta):
        model = AudioAnnotation
        fields = ('id', 'field_name', 'segment', 'status', 'annot_type', 'audio', 'audio_file_format')

class TextAnnotationSerializer(AnnotationSerializer):
    class Meta(AnnotationSerializer.Meta):
        model = TextAnnotation
        fields = ('id', 'field_name', 'segment', 'status', 'annot_type', 'text')

class SpanTextAnnotationSerializer(AnnotationSerializer):
    class Meta(AnnotationSerializer.Meta):
        model = SpanTextAnnotation
        fields = ('id', 'field_name', 'segment', 'status', 'annot_type', 'start', 'end', 'text')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    corpus = serializers.HyperlinkedRelatedField(many=True, view_name='corpus-detail', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'corpus')

# Use the django predefined User class
'''
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus')
'''