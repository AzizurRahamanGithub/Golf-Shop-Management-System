from .models import Booking
from .serializers import BookingSerializer
from ..core.crud import DynamicModelViewSet
from ..core.pagination import CustomPagination
from ..core.permissions import IsAdminRole
from ..core.publicApi import BasePublicAPIView

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Booking
from .serializers import  BookingSerializer, BookingHistorySerializer
from apps.core.response import failure_response, success_response
from apps.cart.models import Cart


import logging

# Set up logging for error handling
logger = logging.getLogger(__name__)

class BookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Get the user's most recent cart or the only active cart
            cart = Cart.objects.filter(user=request.user).order_by('-created_at').first()
            
            if not cart:
                return failure_response(
                    "Cart does not exist.",
                    {},
                    status.HTTP_400_BAD_REQUEST
                )

            if not cart.items.exists():
                return failure_response(
                    "Cart is empty.",
                    {},
                    status.HTTP_400_BAD_REQUEST
                )

            # Initialize serializer with context
            serializer = BookingSerializer(
                data=request.data, 
                context={'request': request, 'cart': cart}  # Pass cart to context
            )

            if serializer.is_valid():
                # Save the booking
                booking = serializer.save(user=request.user)

                # Clear the cart after successful booking
                cart.items.all().delete()

                return success_response(
                    "Booking created successfully.",
                    serializer.data,
                    status.HTTP_201_CREATED
                )

            return failure_response(
                "Invalid data provided",
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Booking creation error: {str(e)}")
            return failure_response(
                "An unexpected error occurred. Please try again later.",
                str(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def get(self, request):
        try:
            # Get all bookings for the current user
            bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
            
            # Pagination (optional)
            paginator = CustomPagination()
            paginated_bookings = paginator.paginate_queryset(bookings, request, view=self)
            
            serializer = BookingSerializer(paginated_bookings, many=True, context={'request': request})
            
            return success_response(
                "Bookings retrieved successfully.",
                  serializer.data,
                status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Bookings list error: {str(e)}")
            return failure_response(
                "An error occurred while retrieving bookings.",
                str(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
            
class BookingDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, booking_id):
        try:
            # Get specific booking for the current user
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            
            serializer = BookingSerializer(booking, context={'request': request})
            
            return success_response(
                "Booking retrieved successfully.",
                serializer.data,
                status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Booking detail error: {str(e)}")
            return failure_response(
                "An error occurred while retrieving the booking.",
                str(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )            
            
            
class BookingHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
            serializer = BookingHistorySerializer(bookings, many=True, context={'request': request})
            return success_response(
                "Booking history retrieved successfully.",
                serializer.data,
                status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Booking history error: {str(e)}")
            return failure_response(
                "An error occurred while fetching booking history.",
                str(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )            