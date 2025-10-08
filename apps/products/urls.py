from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
# router.register(r'features', FeatureViewSet, basename='feature')
router.register(r'packages', PackageViewSet, basename='package')
router.register(r'shops', ShopViewSet, basename='shop')
# router.register(r'reviews', ShopViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    
     path("reviews/", ReviewView.as_view(), name="review-create"),
     path("reviews/<str:product_type>/<int:product_id>/", ReviewListView.as_view(), name="review-list"),
]
