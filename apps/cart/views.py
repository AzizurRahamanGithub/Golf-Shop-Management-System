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


class CartView(APIView):

    def get(self, request):
        try:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            serializer = CartSerializer(cart)
            return success_response(data=serializer.data, message="Cart retrieved successfully.")
        except Cart.DoesNotExist:
            return failure_response(message="Cart not found for the user.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return failure_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            cart = get_object_or_404(Cart, user=request.user)
            cart.items.all().delete()
            return success_response(message="Cart cleared successfully.")
        except Cart.DoesNotExist:
            return failure_response(message="Cart not found for the user.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return failure_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)


class CartItemView(APIView):

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save(cart=cart)
                return success_response(data=serializer.data, message="Item added to cart successfully.", status=status.HTTP_201_CREATED)
            else:
                return failure_response(message="Invalid data provided for the cart item.", status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return failure_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return failure_response(message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            cart = get_object_or_404(Cart, user=request.user)
            item = get_object_or_404(CartItem, cart=cart, pk=pk)
            item.delete()
            return success_response(message="Item removed from cart successfully.")
        except CartItem.DoesNotExist:
            return failure_response(message="Cart item not found.", status=status.HTTP_404_NOT_FOUND)
        except Cart.DoesNotExist:
            return failure_response(message="Cart not found for the user.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return failure_response(message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)