try:
    from django.conf.urls import url
except ImportError:
    from django.urls import url

from notify import views as nf

app_name = 'notifications'


urlpatterns = [
    url(r'^all/$', nf.notifications, name="all"),
    url(r'^api/update/$', nf.notification_update, name="update"),
    url(r'^mark/$', nf.mark, name='mark'),
    url(r'^mark-all/$', nf.mark_all, name='mark_all'),
    url(r'^delete/$', nf.delete, name='delete'),
    url(r'^rdr/(?P<notification_id>[\d]+)/$', nf.read_and_redirect,
        name='read_and_redirect'),
]
