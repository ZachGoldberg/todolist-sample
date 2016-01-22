from rest_framework import serializers
from django.contrib.auth.models import User

from api.models import TodoItem, TodoAttachment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', )


class TodoAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoAttachment
        fields = ('id', 'data')

class TodoItemSerializer(serializers.ModelSerializer):
    attachments = TodoAttachmentSerializer(many=True)

    class Meta:
        model = TodoItem
        fields = ('id', 'title', 'description', 'due_date', 'status', 'owner', 'attachments')

    def create(self, validated_data):
        attachment_data = validated_data.pop('attachments')
        obj = TodoItem.objects.create(**validated_data)
        for attachment in attachment_data:
            tia = TodoAttachment(data=attachment["data"],
                                 todoitem=obj)
            tia.save()
        return obj

    def update(self, obj, validated_data):
        attachment_data = validated_data.pop('attachments')

        for field, value in validated_data.iteritems():
            setattr(obj, field, value)
        obj.save()
        obj.attachments.all().delete()

        for attachment in attachment_data:
            tia = TodoAttachment(data=attachment["data"],
                                 todoitem=obj)
            tia.save()
        return obj
