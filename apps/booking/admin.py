from django.contrib import admin
from .models import Booking, Payment
from django.utils.html import format_html

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'email',
        'shop_type', 'start_date', 'end_date',
        'colored_status',  # এখানে update করো
        'final_total', 'created_at'
    )
    list_filter = ('booking_status', 'shop_type', 'created_at')
    fieldsets = (
        ("Basic Info", {
            'fields': (('user', 'start_date', 'end_date','start_time', 'end_time'),
                       ('booking_status', 'number_of_guests', 'shop_type'))
        }),
        ("Customer Info", {
            'fields': (('full_name', 'email', 'phone', 'street_address'),
                       ('city', 'zip_code'))
        }),
        ("Booking Details", {
            'fields': (('package', 'shop', 'coupon'),
                       ('total_price', 'tax', 'final_total', 'discount_amount'))
        }),
        ("Additional", {
            'fields': (('damage_waiver', 'signature', 'print_name', 'date'),
                       ('signature_image', 'payment_id'))
        }),
    )
    search_fields = ('full_name', 'email', 'phone', 'city', 'shop_type')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def colored_status(self, obj):
        color_map = {
            'completed': '#22c55e',       # green
            'progress': '#f59e0b',        # orange
            'rent started': '#3b82f6',    # blue
        }
        color = color_map.get(obj.booking_status.lower(), '#6b7280')  # default gray
        return format_html(
            '<span style="color: white; background-color: {}; padding: 4px 8px; '
            'border-radius: 6px; font-weight: 500; text-transform: capitalize;">{}</span>',
            color,
            obj.booking_status
        )
    colored_status.short_description = 'Booking Status'

    



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "payment_id", "amount", "colored_status", "method", "created_at")
    list_filter = ("status", "method", "created_at")
    search_fields = ("payment_id", "booking__full_name")
    readonly_fields = ("booking", "payment_id", "amount", "status", "created_at")
    # Fieldsets with proper row alignment
    fieldsets = (
        ("Payment Details", {
            "fields": (
                "booking", "payment_id",          # First row
                ("status", "method","amount", "created_at"),    # Second row
            )
        }),
    )

    def colored_status(self, obj):
        color_map = {
            "completed": "#0D9125",  # তোমার দেওয়া primary green
            "pending": "#f59e0b",    # orange
            "failed": "#ef4444",     # red
        }
        color = color_map.get(obj.status.lower(), "#6b7280")  # default gray
        return format_html(
            '<span style="color: white; background-color: {}; padding: 4px 10px; '
            'border-radius: 6px; font-size: 12px; font-weight: 500; text-transform: capitalize; '
            'box-shadow: 0 0 6px {}80;">{}</span>',
            color,
            color,
            obj.status
        )

    colored_status.short_description = "Status"