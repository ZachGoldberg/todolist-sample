from django.conf.urls import include, url
from rest_framework import routers, serializers, viewsets
from rest_framework.authtoken import views as tokenviews
from api import views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'todoitem', views.TodoItemViewSet)

urlpatterns = [
    url(r'^auth/', tokenviews.obtain_auth_token),
    url(r'^', include(router.urls)),
]
