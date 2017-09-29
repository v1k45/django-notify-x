from django.conf.urls import url
from notify import views as nf

urlpatterns = [
    url(r'^all/$', nf.notifications, name="all"),
    url(r'^api/all/$', nf.NotificationsList.as_view(), name="api_list"),
    url(r'^api/update/$', nf.notification_update, name="update"),
    url(r'^mark/$', nf.mark, name='mark'),
    url(r'^mark-read/$', nf.mark_read, name='mark_read'),
    url(r'^mark-unread/$', nf.mark_unread, name='mark_unread'),
    url(r'^mark-all/$', nf.mark_all, name='mark_all'),
    url(r'^delete/$', nf.delete, name='delete'),
    url(r'^rdr/(?P<notification_id>[\d]+)/$', nf.read_and_redirect,
        name='read_and_redirect'),
]
