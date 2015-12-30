from django_fake_model import models as f
from django.db import models
from django.conf import settings


class Entry(f.FakeModel):
    title = models.CharField(default='This is the title', max_length=30)
    content = models.CharField(default='This is the content', max_length=50)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.title
