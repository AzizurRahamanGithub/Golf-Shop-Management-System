from .models import Booking
from .serializers import BookingSerializer
from ..core.crud import DynamicModelViewSet
from ..core.pagination import CustomPagination
from ..core.permissions import IsAdminRole
from ..core.publicApi import BasePublicAPIView
from django.conf import settings
import stripe


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
stripe.api_key = settings.STRIPE_SECRET_KEY  


class BookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.filter(user=request.user).order_by('-created_at').first()
            if not cart:
                return failure_response("Cart does not exist.", {}, status.HTTP_400_BAD_REQUEST)

            if not cart.items.exists():
                return failure_response("Cart is empty.", {}, status.HTTP_400_BAD_REQUEST)

            pm_id = request.data.get("pm_id")
            if not pm_id:
                return failure_response("Payment method ID (pm_id) is required.", {}, status.HTTP_400_BAD_REQUEST)

            # Calculate total amount from cart
            total_price = sum(item.total_price() for item in cart.items.all())
            amount = int(total_price * 100)  # Stripe uses cents

            # ✅ Create and confirm payment intent
            try:
                intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency="usd",
                    payment_method=pm_id,
                    payment_method_types=["card"],  # only cards
                    confirmation_method="manual",
                    confirm=True,
                )


            except stripe.StripeError as e:
                logger.error(f"Stripe API error: {str(e)}")
                return failure_response(f"Payment error: {e.user_message if hasattr(e, 'user_message') else str(e)}", {}, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Unexpected error with Stripe: {str(e)}")
                return failure_response("Unexpected payment error occurred.", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

            # ✅ Check payment status
            if intent.status not in ["succeeded", "requires_capture"]:
                return failure_response(
                    f"Payment not completed. Status: {intent.status}",
                    {"status": intent.status},
                    status.HTTP_400_BAD_REQUEST,
                )

            # ✅ Create booking record
            serializer = BookingSerializer(
                data=request.data,
                context={'request': request, 'cart': cart}
            )

            if serializer.is_valid():
                booking = serializer.save(
                    user=request.user,
                    payment_id=intent.id  # store Stripe PaymentIntent ID
                )

                # clear cart items after successful booking
                cart.items.all().delete()

                return success_response(
                    "Booking created successfully and payment completed.",
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
                "An unexpected error occurred.",
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