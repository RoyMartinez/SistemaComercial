from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views
from . import documents
from . import ajax
 
urlpatterns=[
    path('',views.index, name='conta_inicio'),
]


if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)