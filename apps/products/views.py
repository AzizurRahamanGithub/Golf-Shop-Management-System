from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from apps.core.response import failure_response, success_response
from rest_framework import status

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
        

# class FeatureViewSet(DynamicModelViewSet):
#     queryset = Feature.objects.all()
#     serializer_class = FeatureSerializer
#     permission_classes = [IsAuthenticated]
 
#     def __init__(self, *args, **kwargs):
#         kwargs['model'] = Feature
#         kwargs['serializer_class'] = FeatureSerializer
#         kwargs['item_name'] = 'Feature'
#         super().__init__(*args, **kwargs)

class PackageViewSet(DynamicModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        kwargs['model'] = Package
        kwargs['serializer_class'] = PackageSerializer
        kwargs['item_name'] = 'Package'
        super().__init__(*args, **kwargs)

    @action(detail=True, methods=["delete"], url_path="features/(?P<feature_id>[^/.]+)")
    def delete_feature(self, request, pk=None, feature_id=None):
        package = get_object_or_404(Package, pk=pk)
        feature = get_object_or_404(Feature, pk=feature_id)
        
        # Check if the feature belongs to this package
        if feature not in package.features.all():
            return failure_response(
                {"error": "This feature does not belong to this package."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete the feature
        feature.delete()
        return success_response(
            { f"Feature '{feature.name}' deleted from package '{package.name}'."},
            status=status.HTTP_200_OK
        )          
                        

class ShopViewSet(DynamicModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]
 
    def __init__(self, *args, **kwargs):
        kwargs['model'] = Shop
        kwargs['serializer_class'] = ShopSerializer
        kwargs['item_name'] = 'Shop'
        super().__init__(*args, **kwargs)       
        
                         