from rest_framework import serializers
from django.contrib.auth.models import User

from api.models import TodoItem, TodoAttachment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', )

class TodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = ('title', 'description', 'due_date', 'status', 'owner')


class TodoAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoAttachment
        fields = ('data', 'todoitem_id')
