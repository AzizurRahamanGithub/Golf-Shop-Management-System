from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from apps.core.crud import DynamicModelViewSet

class CategoryViewSet(DynamicModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
 
    def __init__(self, *args, **kwargs):
        kwargs['model'] = Category
        kwargs['serializer_class'] = CategorySerializer
        kwargs['item_name'] = 'Category'
        super().__init__(*args, **kwargs)
        

class FeatureViewSet(DynamicModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [IsAuthenticated]
 
    def __init__(self, *args, **kwargs):
        kwargs['model'] = Feature
        kwargs['serializer_class'] = FeatureSerializer
        kwargs['item_name'] = 'Feature'
        super().__init__(*args, **kwargs)

class PackageViewSet(DynamicModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]
 
    def __init__(self, *args, **kwargs):
        kwargs['model'] = Package
        kwargs['serializer_class'] = PackageSerializer
        kwargs['item_name'] = 'Package'
        super().__init__(*args, **kwargs)
                        

class ShopViewSet(DynamicModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]
 
    def __init__(self, *args, **kwargs):
        kwargs['model'] = Shop
        kwargs['serializer_class'] = ShopSerializer
        kwargs['item_name'] = 'Shop'
        super().__init__(*args, **kwargs)                        