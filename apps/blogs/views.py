from .models import Blog
from .serializers import BlogSerializer
from ..core.crud import DynamicModelViewSet
from ..core.pagination import CustomPagination
from ..core.permissions import IsAdminRole
from ..core.publicApi import BasePublicAPIView
from rest_framework.permissions import IsAuthenticated
from apps.notification.utils import notify_admins
from apps.core.response import failure_response, success_response
import random
from rest_framework import generics
from rest_framework.views import APIView


class RandomBlogListView(APIView):
    def get(self, request):
        # only published blogs
        blogs = Blog.objects.filter(blog_status='published')
        random_blogs = random.sample(list(blogs), min(len(blogs), 10))
        serializer = BlogSerializer(random_blogs, many=True)
        return success_response("Random blogs retrieved successfully", serializer.data)

class BlogListView(APIView):
    def get(self, request):
        # only published blogs
        blogs = Blog.objects.filter(blog_status='published')
        serializer = BlogSerializer(blogs, many=True)
        return success_response("Blogs retrieved successfully", serializer.data)


class BlogViewSet(DynamicModelViewSet):
    queryset = Blog.objects.filter(blog_status='published')  # only published
    serializer_class = BlogSerializer

    def __init__(self, *args, **kwargs):
        kwargs['model'] = Blog
        kwargs['serializer_class'] = BlogSerializer
        kwargs['item_name'] = 'Blog'
        super().__init__(*args, **kwargs)

    def perform_create(self, serializer):
        blog = super().perform_create(serializer)
        self._notify_status(blog)
        return blog

    def perform_update(self, serializer):
        blog = super().perform_update(serializer)
        self._notify_status(blog)
        return blog

    def _notify_status(self, blog):
        from apps.notification.utils import notify_admins

        if blog.blog_status == "pending":
            notify_admins("New Blog Pending Approval", f"'{blog.title}' is awaiting review.")
        elif blog.blog_status == "published":
            notify_admins("New Blog Published", f"A new blog '{blog.title}' has been published.")
        elif blog.blog_status == "draft":
            notify_admins("New Draft Created", f"A draft blog '{blog.title}' has been created.")
