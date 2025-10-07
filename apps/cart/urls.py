from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CartView, CartItemView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path("cart/items/", CartItemView.as_view(), name="cart-item-add"),
    path("cart/items/<int:pk>/", CartItemView.as_view(), name="cart-item-remove")
]
