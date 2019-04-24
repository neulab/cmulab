from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.schemas import get_schema_view
from speech import views

schema_view = get_schema_view(title='Pastebin API')

urlpatterns = [
    path('schema/', schema_view),
    #path('speech/', views.snippet_list),
    path('speech/', views.api_root),
    path('speech/model/', views.ModelList.as_view(), name='model-list'),
    path('speech/model/<int:pk>/', views.ModelDetail.as_view(), name='model-detail'),
    #path('speech/model/findByTags/', views.model_list_by_tags),
    #path('speech/model/findByStatus/', views.model_list_by_status),
    path('speech/corpus/', views.CorpusList.as_view(), name='corpus-list'),
    path('speech/corpus/<int:pk>/', views.CorpusDetail.as_view(), name='corpus-detail'),
    path('speech/corpus/<int:pk>/segments/', views.SegmentsInCorpus.as_view(), name='corpussegment-list'),
    path('speech/corpus/<int:pk>/addsegments/<str:s_list>/', views.addsegmentstocorpus, name='corpussegment-add'),
    path('speech/corpus/<int:pk>/removesegments/<str:s_list>/', views.removesegmentsfromcorpus, name='corpussegment-add'),

    path('speech/segment/', views.SegmentList.as_view(), name='segment-list'),
    path('speech/segment/<int:pk>/', views.SegmentDetail.as_view(), name='segment-detail'),
    path('speech/segment/<int:pk>/annotations/', views.AnnotationsInSegment.as_view(), name='annotationsegment-detail'),
    path('speech/annotation/', views.AnnotationList.as_view(), name='annotation-list'),
    path('speech/annotation/<int:pk>/', views.AnnotationDetail.as_view(), name='annotation-detail'),
    path('speech/textannotation/', views.TextAnnotationList.as_view(), name='textannotation-list'),
    path('speech/textannotation/<int:pk>/', views.TextAnnotationDetail.as_view(), name='textannotation-detail'),
    path('speech/audioannotation/', views.AudioAnnotationList.as_view(), name='audioannotation-list'),
    path('speech/audioannotation/<int:pk>/', views.AudioAnnotationDetail.as_view(), name='audioannotation-detail'),
    path('speech/spantextannotation/', views.SpanTextAnnotationList.as_view(), name='spantextannotation-list'),
    path('speech/spantextannotation/<int:pk>/', views.SpanTextAnnotationDetail.as_view(), name='spantextannotation-detail'),
    path('users/', views.UserList.as_view(), name='user-list'),
	path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    

]

urlpatterns = format_suffix_patterns(urlpatterns)
