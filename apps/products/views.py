from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from apps.core.response import failure_response, success_response
from rest_framework import status
from rest_framework import permissions, status
from rest_framework.views import APIView

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
        
        
import logging

logger = logging.getLogger(__name__)


class ReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Create a new review for a shop or package.
        """
        try:
            serializer = ReviewSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return success_response(
                    "Review submitted successfully.",
                    serializer.data,
                    status.HTTP_201_CREATED
                )

            return failure_response(
                "Invalid data.",
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Review creation error: {str(e)}")
            return failure_response(
                "An error occurred while submitting review.",
                str(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def get(self, request):
        """
        Retrieve all reviews submitted by the logged-in user
        """
        try:
            user = request.user
            reviews = Review.objects.filter(user=user).order_by('-created_at')
            serializer = ReviewSerializer(reviews, many=True, context={'request': request})
            
            return success_response(
                "User reviews retrieved successfully.",  # message
                serializer.data,                        # data
                status.HTTP_200_OK                       # status code
            )
        except Exception as e:
            logger.error(f"User reviews retrieval error: {str(e)}")
            return failure_response(
                "An error occurred while fetching your reviews.",  # message
                str(e),                                           # data / error
                status.HTTP_500_INTERNAL_SERVER_ERROR            # status code
            )


class ReviewListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_type, product_id):
        """
        List reviews for a specific shop or package
        """
        try:
            if product_type == "shop":
                reviews = Review.objects.filter(shop_id=product_id)
            elif product_type == "package":
                reviews = Review.objects.filter(package_id=product_id)
            else:
                return failure_response(
                     "Invalid product type.",
                     {}
                )

            serializer = ReviewSerializer(reviews, many=True, context={'request': request})
            return success_response(
                 "Reviews retrieved successfully.",
                 serializer.data
            )

        except Exception as e:
            logger.error(f"Booking history error: {str(e)}")
            return failure_response(
                "An error occurred while fetching booking history.",
                str(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )      