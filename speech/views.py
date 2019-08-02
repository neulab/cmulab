
from django.contrib.auth.models import User
from django.shortcuts import render

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics
from rest_framework import status
from rest_framework import permissions

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from speech.models import Mlmodel, Corpus, Segment
from speech.models import Annotation, TextAnnotation, AudioAnnotation, SpanTextAnnotation

from speech.permissions import IsOwnerOrReadOnly

from speech.serializers import MlmodelSerializer, CorpusSerializer, SegmentSerializer, UserSerializer
from speech.serializers import AnnotationSerializer, AudioAnnotationSerializer, TextAnnotationSerializer, SpanTextAnnotationSerializer

from speech.BackendModels import MLModels

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

@api_view(['POST'])
def trainModel(request, pk):
	try:
		mlmodel = Mlmodel.objects.get(pk=pk)
	except Mlmodel.DoesNotExist:
		raise Http404

	if request.method == 'POST':
		return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET', 'PUT'])
def annotate(request, mk, sk):
	#mk is the model id
	#sk is the segment id	
	try:
		segment = Segment.objects.get(pk=sk)
	except Segment.DoesNotExist:
		raise Http404

	try:
		model = Mlmodel.objects.get(pk=mk)
	except Mlmodel.DoesNotExist:
		raise Http404

	if request.method == 'GET':
		annot = Annotation.objects.filter(segment=segment.id)
		serializer = AnnotationSerializer(annot)
		return Response(serializer.data)

	elif request.method == 'PUT':
		try:
			# First retrieve the model details
			modeltag = model.tags
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
	#	serializer.save(owner=self.request.user)

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

class ModelDetail(generics.RetrieveUpdateAPIView):
	queryset = Mlmodel.objects.all()
	serializer_class = MlmodelSerializer


class AnnotationList(generics.ListCreateAPIView):
	queryset = Annotation.objects.all()
	serializer_class = AnnotationSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('status', 'segment',)

class AnnotationDetail(generics.RetrieveUpdateAPIView):
	queryset = Annotation.objects.all()
	serializer_class = AnnotationSerializer

class AudioAnnotationList(generics.ListCreateAPIView):
	queryset = AudioAnnotation.objects.all()
	serializer_class = AudioAnnotationSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('status', 'segment', )

class AudioAnnotationDetail(generics.RetrieveUpdateAPIView):
	queryset = AudioAnnotation.objects.all()
	serializer_class = AudioAnnotationSerializer

class TextAnnotationList(generics.ListCreateAPIView):
	queryset = TextAnnotation.objects.all()
	serializer_class = TextAnnotationSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('status', 'segment',)

class TextAnnotationDetail(generics.RetrieveUpdateAPIView):
	queryset = TextAnnotation.objects.all()
	serializer_class = TextAnnotationSerializer

class SpanTextAnnotationList(generics.ListCreateAPIView):
	queryset = SpanTextAnnotation.objects.all()
	serializer_class = SpanTextAnnotationSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('status', 'segment',)

class SpanTextAnnotationDetail(generics.RetrieveUpdateAPIView):
	queryset = SpanTextAnnotation.objects.all()
	serializer_class = SpanTextAnnotationSerializer



# Generic API views
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

