from django.shortcuts import render
from django.contrib.auth.models import User
from api.models import TodoItem, TodoAttachment
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from api.serializers import (UserSerializer, TodoItemSerializer,
                                  TodoAttachmentSerializer)



class AnonCreatePermission(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_object_permission(self, request, view, obj):
        # allow anybody to create a user
        if request.method == 'POST':
            return True

        # But you can only read yourself
        if request.method in permissions.SAFE_METHODS and obj == request.user:
            return True

        # And you can edit/delete yourself
        if request.method in ['PUT', 'DELETE'] and obj == request.user:
            return True

        return False

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (AnonCreatePermission, )
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def create(self, request):
        user = User()
        user.username = request.data.get('username')
        user.set_password(request.data.get('password'))
        user.save()
        return Response({'status': 'OK'},
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        try:
            uid = int(pk)
        except:
            try:
                uid = User.objects.get(username=pk).id
            except:
                raise exceptions.APIException

        if request.user.id != uid:
            raise exceptions.PermissionDenied

        TodoItem.objects.filter(owner_id=uid).delete()
        self.kwargs['pk'] = uid
        return super(UserViewSet, self).destroy(request, uid)

class TodoItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TodoItems to be viewed or edited.
    """
    permission_classes = (IsAuthenticated, )
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer
    def create(self, request):
        request.data['owner'] = request.user.id
        return super(TodoItemViewSet, self).create(request)

    def update(self, request, pk=None):
        ti = TodoItem.objects.get(id=pk)
        if ti.owner != request.user:
            raise exceptions.PermissionDenied

        request.data['owner'] = request.user.id
        return super(TodoItemViewSet, self).update(request, pk=pk)

class TodoAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TodoAttachments to be viewed or edited.
    """
    queryset = TodoAttachment.objects.all()
    serializer_class = TodoAttachmentSerializer
