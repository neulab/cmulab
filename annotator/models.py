# -*- coding: utf-8 -*-

import os
import datetime

from django.db import models
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import allosaurus
import traceback
import shutil

MEDIA_ROOT = getattr(settings, "MEDIA_ROOT", "/tmp")



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    consent = models.BooleanField(default=False)

class Document(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, null = True, on_delete=models.CASCADE)
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class Transcript(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, null = True, on_delete=models.CASCADE)
    filename = models.CharField(max_length=200, blank=True, default='', help_text='filename')
    text = models.TextField(max_length=10000, help_text='TBD')

class Mlmodel(models.Model):
    '''
    Operations about annotation models
    '''
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null = True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200, blank=True, default='', help_text='generic name of the model')
    created = models.DateTimeField(auto_now_add=True, help_text='')
    modelTrainingSpec = models.TextField(max_length=10000, help_text='TBD')
    model_path = models.CharField(max_length=10000, default='', help_text='model file / dir path')
    log_file = models.CharField(max_length=10000, default='', help_text='log file path')

    QUEUED = 'queued'
    TRAIN = 'training'
    READY = 'ready'
    UNAVAILABLE = 'unavailable'
    STATUS_CHOICES = [(QUEUED, 'queued'), (TRAIN, 'training'), (READY, 'ready'), (UNAVAILABLE, 'unavailable')]
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=UNAVAILABLE, help_text='')

    VAD = "vad"
    TRANSCRIPTION = "transcription"
    TRANSLATION = "translation"
    MORPHOLOGY = "morphology"
    OTHER = "other"
    TAG_CHOICES = [(VAD, "vad"), (TRANSCRIPTION, "transcription"), (TRANSLATION, "translation"), (MORPHOLOGY, "morphology"), (OTHER, "other")]
    tags = models.CharField(choices=TAG_CHOICES, max_length=20, default=OTHER, help_text='a tag for the model type, in order to be filtered by')

    class Meta:
        ordering = ('created', 'id',)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        try:
            fs = FileSystemStorage()
            # TODO: store the log/working dir paths in mlmodel
            if self.modelTrainingSpec == "allosaurus":
                fs.delete("allosaurus_finetune_" + self.name + "_log.txt")
                shutil.rmtree(str(allosaurus.model.get_model_path(self.name)))
            elif self.modelTrainingSpec == "ocr-post-correction":
                print("Deleting " + os.path.join(MEDIA_ROOT, self.name))
                shutil.rmtree(os.path.join(MEDIA_ROOT, self.name))
            try:
                os.remove(self.log_file)
            except:
                tb = traceback.format_exc()
                print(tb)
        except:
            tb = traceback.format_exc()
            print(tb)
        super().delete(*args, **kwargs)


class Corpus(models.Model):
    '''
    Operations about corpora of linguistic data
    '''
    name = models.CharField(max_length=200, blank=True, default='', help_text='The corpus (collection of segments)')
    owner = models.ForeignKey('auth.User', related_name='corpus', on_delete=models.CASCADE, default=1)
    # The list of segments is found be the serializer
    #segments = models.TextField(blank=True)
    class Meta:
        ordering = ('id',)


class Segment(models.Model):
    '''
    Operations about segments of linguistic data
    '''
    name = models.CharField(max_length=100, blank=True, null=True, help_text='the name of this segment')
    # Each segment is a member of a corpus and segment.corpus_id can retrieve it
    corpus = models.ForeignKey('Corpus', related_name='segment', on_delete=models.CASCADE, blank=True, null=True, help_text='The corpus that this segment corresponds to. (foreign key)')

    class Meta:
        ordering = ('id',)

    # The list of annotations is defined in the serializers
    # One could however use a Segment ForeignKey within the Annotation classes
    #annotations = models.TextField(blank=True)

    #audio = models.FileField(upload_to='audios/')
    #pub_date = models.DateTimeField(auto_now_add=True)
    #vad = models.TextField(max_length=1000, blank=True)
    #phone_boundaries = models.TextField(max_length=10000, blank=True)
    #spectrum_path = models.TextField(max_length=1000, blank=True)


class Annotation(models.Model):
    '''
    Generic anotation class
    '''
    field_name = models.CharField(max_length=100, help_text='The name of the field within the segment', blank=True, null=True)
    segment = models.ForeignKey('Segment', related_name='annotation', blank=True, null=True, on_delete=models.CASCADE, help_text='The segment that this annotation corresponds to. (foreign key)')
    CORRECT = 'correct'
    INCORRECT = 'incorrect'
    GENERATED = 'generated'
    UNKNOWN = 'unknown'
    STATUS_CHOICES = [(CORRECT, 'correct'), (INCORRECT, 'incorrect'), (GENERATED, 'generated'), (UNKNOWN, 'unknown')]
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=UNKNOWN, help_text='describes the status of the annotation e.g. correct/incorrect, or generated by a backend model (but not checked), or unknown', blank=True, null=True)

    class Meta:
        ordering = ('id',)


# This is for storing audio annotations (audio files)
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class AudioAnnotation(Annotation):
    # Audio Annotation
    #audio = models.FileField(upload_to=user_directory_path, help_text='An audio file for the segment')
    audio = models.FileField(upload_to=user_directory_path, help_text='An audio file for the segment')
    WAV = 'wav'
    MP3 = 'mp3'
    AUDIO_FILE_CHOICES = [(WAV, 'wav'), (MP3, 'mp3')] # This needs to be a list of tuples
    audio_file_format = models.CharField(choices=AUDIO_FILE_CHOICES, max_length=10, help_text='An indicator of the audio file format')
    annot_type = "audio"

class TextAnnotation(Annotation):
    # Text Annotation
    text = models.TextField(max_length=100, help_text='A single textual string describing the whole segment')
    annot_type = "text"

class SpanTextAnnotation(Annotation):
    # Span Text Annotation
    # The following is not needed cause inheritance
    #source_field = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    start = models.FloatField(help_text='Start of the span with respect to the source field (e.g in seconds or indices)')
    end = models.FloatField(help_text='End of the span with respect to the source field (e.g in seconds or indices)')
    text = models.TextField(max_length=100, help_text='annotation of the span')
    annot_type = "spantext"



# Use django's predefined User class for now
'''
class User(models.Model):
    username = models.CharField(max_length=100, blank=False, default='', help_text='username')
    firstName = models.CharField(max_length=100, blank=False, default='', help_text='first name')
    lastName = models.CharField(max_length=100, blank=False, default='', help_text='last name')
    email = models.EmailField(blank=False, default='', help_text='email')
    password = models.CharField(max_length=100, blank=False, default='', help_text='password (store encrypted?)')
    phone = models.CharField(max_length=100, blank=False, default='', help_text='phone')
    ADMIN = 0
    USER = 1
    STATUS_CHOICES = [(ADMIN, 'ADMIN'), (USER, 'USER')] # 0 : admin, 1: user -- not sure how to make these integer
    userStatus = models.IntegerField(choices=STATUS_CHOICES, default=USER, help_text='User Status. 0 : admin, 1: user')
'''
