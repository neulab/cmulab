from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', include('snippets.urls')),
    path('', include('speech.urls')),
]

# This is for the login information in the beginning
urlpatterns += [
    path('speech/', include('rest_framework.urls')),
]
