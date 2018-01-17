from django.urls import path, include
from .. import urls

urlpatterns = ([
    path('', include(urls, namespace='notifications'))
])
