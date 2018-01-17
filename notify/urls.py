from django.conf.urls import url
from django.urls import path
from .views import *

app_name = 'notifications'
urlpatterns = [
    path('all/', notifications, name="all"),
    path('api/update/', notification_update, name="update"),
    path('mark/', mark, name='mark'),
    path('mark-all/', mark_all, name='mark_all'),
    path('delete/', delete, name='delete'),
    url(r'^rdr/(?P<notification_id>[\d]+)/$', read_and_redirect,
        name='read_and_redirect'),
]
