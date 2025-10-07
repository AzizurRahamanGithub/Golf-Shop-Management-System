from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BookingView, BookingDetailView


urlpatterns = [
    path('summery/', BookingView.as_view(), name='booking-create'),
    path('<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
]
