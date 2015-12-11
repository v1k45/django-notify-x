from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('notify.urls', namespace='notifications')),
]
