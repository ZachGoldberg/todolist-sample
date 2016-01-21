from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class TodoItem(models.Model):
    class Meta:
        app_label = 'api'

    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    owner = models.ForeignKey(User)

class TodoAttachment(models.Model):
    class Meta:
        app_label = 'api'

    data = models.TextField()
    todoitem = models.ForeignKey('TodoItem')
