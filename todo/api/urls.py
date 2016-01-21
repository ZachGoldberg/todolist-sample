from django.conf.urls import include, url
from rest_framework import routers, serializers, viewsets

from api import views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'todoitem', views.TodoItemViewSet)
router.register(r'todoattachment', views.TodoAttachmentViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
