from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'public', BlogViewSet, basename='blog')

urlpatterns = [
    path('', include(router.urls)),
     path('random/blogs/', RandomBlogListView.as_view(), name='random-blogs'),
     path('blogs/', BlogListView.as_view(), name='blogs'),
]
