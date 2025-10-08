from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BookingView, BookingDetailView, BookingHistoryView


urlpatterns = [
    path('summery/', BookingView.as_view(), name='booking-create'),
    path('summery/<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
    path("summery/history/", BookingHistoryView.as_view(), name="booking-history"),
]
