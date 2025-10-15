from django.contrib import admin
from .models import Booking, Payment

@admin.register(Booking)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "booking_status", "final_total", "created_at")
    list_filter = ("booking_status", "created_at")
    search_fields = ("full_name", "email", "phone")
    readonly_fields = ("payment_id", "final_total", "created_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "payment_id", "amount", "status", "method", "created_at")
    list_filter = ("status", "method", "created_at")
    search_fields = ("payment_id", "booking__full_name")
    readonly_fields = ("booking", "payment_id", "amount", "status", "created_at")