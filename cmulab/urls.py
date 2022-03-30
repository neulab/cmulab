from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="index.html")),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),
    path('', include('annotator.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]

# This is for the login information in the beginning
urlpatterns += [
    path('annotator/', include('rest_framework.urls')),
]

urlpatterns += [
    path('django-rq/', include('django_rq.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
