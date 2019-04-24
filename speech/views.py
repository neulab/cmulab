
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


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'corpus': reverse('corpus-list', request=request, format=format)
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
			segment.save()
			segment_list.append(segment)

		serializer = SegmentSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			#return Response(serializer.data)

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
		for s_id in segment_ids:
			try:
				segment = Segment.objects.get(pk=s_id)
			except Segment.DoesNotExist:
				raise Http404
			segment.corpus=None
			segment.save()
			segment_list.append(segment)

		serializer = SegmentSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			#return Response(serializer.data)


# Views for Segments
class SegmentList(APIView):
	"""
	List all segments, or create a new segment
	"""
	# This makes sure that only authenticated requests get served
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get(self, request, format=None):
		segment = Segment.objects.all()
		serializer = SegmentSerializer(segment, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		segment = Segment.get_object(pk)
		serializer = SegmentSerializer(data=request.data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	# This ties the corpus to its owner (User)
	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class SegmentDetail(APIView):
	"""
	Retrieve, update or delete a segment.
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
		serializer = SegmentSerializer(segment)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		segment = self.get_object(pk)
		serializer = SegmentSerializer(segment, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):
		segment = self.get_object(pk)
		segment.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

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





# These generic API views for annotations work too
class ModelList(generics.ListAPIView):
	queryset = Mlmodel.objects.all()
	serializer_class = MlmodelSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('status', 'tags')

class ModelDetail(generics.RetrieveAPIView):
	queryset = Mlmodel.objects.all()
	serializer_class = MlmodelSerializer


class AnnotationList(generics.ListAPIView):
	queryset = Annotation.objects.all()
	serializer_class = AnnotationSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('status',)

class AnnotationDetail(generics.RetrieveAPIView):
	queryset = Annotation.objects.all()
	serializer_class = AnnotationSerializer

class AudioAnnotationList(generics.ListAPIView):
	queryset = AudioAnnotation.objects.all()
	serializer_class = AudioAnnotationSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('status',)

class AudioAnnotationDetail(generics.RetrieveAPIView):
	queryset = AudioAnnotation.objects.all()
	serializer_class = AudioAnnotationSerializer

class TextAnnotationList(generics.ListAPIView):
	queryset = TextAnnotation.objects.all()
	serializer_class = TextAnnotationSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('status',)

class TextAnnotationDetail(generics.RetrieveAPIView):
	queryset = TextAnnotation.objects.all()
	serializer_class = TextAnnotationSerializer

class SpanTextAnnotationList(generics.ListAPIView):
	queryset = SpanTextAnnotation.objects.all()
	serializer_class = SpanTextAnnotationSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('status',)

class SpanTextAnnotationDetail(generics.RetrieveAPIView):
	queryset = SpanTextAnnotation.objects.all()
	serializer_class = SpanTextAnnotationSerializer



# Generic API views
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

