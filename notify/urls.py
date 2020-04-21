try:
    from django.conf.urls import path
except ImportError:
    from django.urls import path

from notify import views as nf

app_name = 'notifications'


urlpatterns = [
    path('all/', nf.notifications, name="all"),
    path('api/update/', nf.notification_update, name="update"),
    path('mark/', nf.mark, name='mark'),
    path('mark-all/', nf.mark_all, name='mark_all'),
    path('delete/<int:notification_id>/', nf.delete, name='delete'),
    path('delete/', nf.delete, name='delete'),
    path('rdr/<int:notification_id>/', nf.read_and_redirect,
        name='read_and_redirect'),
]

