# apps/custom_home/context_processors.py
from django.db.models import Sum
from apps.booking.models import Booking
from apps.auths.models import CustomUser

def dashboard_metrics(request):
    return {
        "total_bookings": Booking.objects.filter(booking_status='completed').count(),
        "total_users": CustomUser.objects.filter(role='user').count(),
        "total_earning": Booking.objects.filter(booking_status='completed').aggregate(total=Sum('final_total'))['total'] or 0,
        "total_rental": Booking.objects.filter(shop_type__isnull=False).count(),
    }
