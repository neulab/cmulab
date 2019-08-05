

# Views for Segments
class SegmentList1(APIView):
	"""
	List all segments, or create a new segment
	"""
	# This makes sure that only authenticated requests get served
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	filter_backends = (DjangoFilterBackend,)
	filterset_fields = ('corpus',)

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


class SegmentDetail1(APIView):
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

# Generic Views for Annotations
class AnnotationList(APIView):
	"""
	List all annotations in a corpus, or create a new annotation
	"""
	# This makes sure that only authenticated requests get served
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get(self, request, format=None):
		annot = Annotation.objects.all()
		serializer = AnnotationSerializer(annot, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		annot = Annotation.get_object(pk)
		serializer = AnnotationSerializer(data=request.data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	# This ties the corpus to its owner (User)
	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class AnnotationDetail(APIView):
	"""
	Retrieve, update or delete an annotation.
	"""
	# This makes sure that only authenticated requests get served
	# and that only the Owner of a corpus can modify it
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get_object(self, pk):
		try:
			return Annotation.objects.get(pk=pk)
		except Annotation.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		annot = self.get_object(pk)
		serializer = AnnotationSerializer(annot)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		annot = self.get_object(pk)
		serializer = AnnotationSerializer(annot, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):
		annot = self.get_object(pk)
		annot.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)




# Views for Audio Annotations
class AudioAnnotationList1(APIView):
	"""
	List all audio annotations in a corpus, or create a new audio annotation
	"""
	# This makes sure that only authenticated requests get served
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get(self, request, format=None):
		annot = AudioAnnotation.objects.all()
		serializer = AudioAnnotationSerializer(annot, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		annot = AudioAnnotation.get_object(pk)
		serializer = AudioAnnotationSerializer(data=request.data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	# This ties the corpus to its owner (User)
	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class AudioAnnotationDetail1(APIView):
	"""
	Retrieve, update or delete an audio annotation.
	"""
	# This makes sure that only authenticated requests get served
	# and that only the Owner of a corpus can modify it
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get_object(self, pk):
		try:
			return AudioAnnotation.objects.get(pk=pk)
		except AudioAnnotation.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		annot = self.get_object(pk)
		serializer = AudioAnnotationSerializer(annot)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		annot = self.get_object(pk)
		serializer = AudioAnnotationSerializer(annot, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):
		annot = self.get_object(pk)
		annot.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

# Views for Text Annotations
class TextAnnotationList1(APIView):
	"""
	List all annotations in a corpus, or create a new annotation
	"""
	# This makes sure that only authenticated requests get served
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get(self, request, format=None):
		annot = TextAnnotation.objects.all()
		serializer = TextAnnotationSerializer(annot, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		annot = TextAnnotation.get_object(pk)
		serializer = TextAnnotationSerializer(data=request.data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	# This ties the corpus to its owner (User)
	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class TextAnnotationDetail1(APIView):
	"""
	Retrieve, update or delete an annotation.
	"""
	# This makes sure that only authenticated requests get served
	# and that only the Owner of a corpus can modify it
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get_object(self, pk):
		try:
			return TextAnnotation.objects.get(pk=pk)
		except TextAnnotation.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		annot = self.get_object(pk)
		serializer = TextAnnotationSerializer(annot)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		annot = self.get_object(pk)
		serializer = TextAnnotationSerializer(annot, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):
		annot = self.get_object(pk)
		annot.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)



# Views for Span Text Annotations
class SpanTextAnnotationList1(APIView):
	"""
	List all annotations in a corpus, or create a new annotation
	"""
	# This makes sure that only authenticated requests get served
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get(self, request, format=None):
		annot = SpanTextAnnotation.objects.all()
		serializer = SpanTextAnnotationSerializer(annot, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		annot = SpanTextAnnotation.get_object(pk)
		serializer = SpanTextAnnotationSerializer(data=request.data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	# This ties the corpus to its owner (User)
	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class SpanTextAnnotationDetail1(APIView):
	"""
	Retrieve, update or delete an annotation.
	"""
	# This makes sure that only authenticated requests get served
	# and that only the Owner of a corpus can modify it
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get_object(self, pk):
		try:
			return SpanTextAnnotation.objects.get(pk=pk)
		except SpanTextAnnotation.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		annot = self.get_object(pk)
		serializer = SpanTextAnnotationSerializer(annot)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		annot = self.get_object(pk)
		serializer = SpanTextAnnotationSerializer(annot, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):
		annot = self.get_object(pk)
		annot.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)