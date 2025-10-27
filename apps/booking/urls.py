from django.urls import path
from .views import (
    CreatePaymentIntentView,
    ConfirmBookingView,
    BookingView,
    BookingDetailView,
    BookingHistoryView,
)

urlpatterns = [
    # -----------------------------
    # Payment-related endpoints
    # -----------------------------
    path("payments/create-intent/", CreatePaymentIntentView.as_view(), name="create-payment-intent"),
    path("payments/confirm-booking/", ConfirmBookingView.as_view(), name="confirm-booking"),

    # -----------------------------
    # Booking endpoints
    # -----------------------------
    path("summery/", BookingView.as_view(), name="booking-list"),  # list user bookings
    path("summery/<int:booking_id>/", BookingDetailView.as_view(), name="booking-detail"),
    path("summery/history/", BookingHistoryView.as_view(), name="booking-history"),
]
