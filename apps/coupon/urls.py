from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CouponViewSet, UserSearchView, SendMultipleCouponsView

router = DefaultRouter()
router.register(r'manage', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    path('send-coupon/', SendMultipleCouponsView.as_view(), name='send-multiple-coupons'),
]
