from django.conf.urls import url
from notify import views as nf

urlpatterns = [
    url(r'^all/$', nf.notifications, name="all"),
    url(r'^api/update/$', nf.notification_update, name="update"),
    url(r'^mark/$', nf.mark, name='mark'),
    url(r'^mark-all/$', nf.mark_all, name='mark_all'),
    url(r'^delete/$', nf.delete, name='delete'),
]
