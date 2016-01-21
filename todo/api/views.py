from django.shortcuts import render
from django.contrib.auth.models import User
from api.models import TodoItem, TodoAttachment
from rest_framework import viewsets

from api.serializers import (UserSerializer, TodoItemSerializer,
                                  TodoAttachmentSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class TodoItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TodoItems to be viewed or edited.
    """
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer

class TodoAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TodoAttachments to be viewed or edited.
    """
    queryset = TodoAttachment.objects.all()
    serializer_class = TodoAttachmentSerializer
