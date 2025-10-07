from .models import Blog
from .serializers import BlogSerializer
from ..core.crud import DynamicModelViewSet
from ..core.pagination import CustomPagination
from ..core.permissions import IsAdminRole
from ..core.publicApi import BasePublicAPIView
from rest_framework.permissions import IsAuthenticated
   

class BlogViewSet(DynamicModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        kwargs['model'] = Blog
        kwargs['serializer_class'] = BlogSerializer
        kwargs['item_name'] = 'Blog'
        super().__init__(*args, **kwargs)

