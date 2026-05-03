from apps.cart.utils import get_or_create_cart
from .models import Cart
from .serializers import CartSerializer
from ..core.crud import DynamicModelViewSet
from ..core.pagination import CustomPagination
from ..core.permissions import IsAdminRole
from ..core.publicApi import BasePublicAPIView

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.core.response import failure_response, success_response
from rest_framework.exceptions import NotFound, ValidationError


from apps.cart.utils import get_or_create_cart

class CartView(APIView):

    def get(self, request):
        try:
            cart = get_or_create_cart(request)   # 🔥 change এখানে
            serializer = CartSerializer(cart)
            return success_response(
                data=serializer.data,
                message="Cart retrieved successfully."
            )
        except Exception as e:
            return failure_response(message=str(e))

    def delete(self, request):
        try:
            cart = get_or_create_cart(request)   # 🔥 change এখানে
            cart.items.all().delete()
            return success_response(message="Cart cleared successfully.")
        except Exception as e:
            return failure_response(message=str(e))


class CartItemView(APIView):

    def post(self, request):
        try:
            cart = get_or_create_cart(request)   # 🔥 change এখানে

            serializer = CartItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(cart=cart)
                return success_response(
                    data=serializer.data,
                    message="Item added to cart successfully.",
                    status=201
                )

            return failure_response(message=serializer.errors)

        except Exception as e:
            return failure_response(message=str(e))

    def delete(self, request, pk):
        try:
            cart = get_or_create_cart(request)   # 🔥 change এখানে
            item = get_object_or_404(CartItem, cart=cart, pk=pk)
            item.delete()
            return success_response(message="Item removed from cart successfully.")
        except Exception as e:
            return failure_response(message=str(e))