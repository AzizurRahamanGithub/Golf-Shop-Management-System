from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin
from apps.booking.models import Booking
from apps.auths.models import CustomUser
from django.db.models import Sum


class AdminDashboardView(UnfoldModelAdminViewMixin, TemplateView):
    template_name = "dashboard.html"
    title = "Admin Dashboard"
    permission_required = ()  # set permissions if needed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add your metrics
        context['total_bookings'] = Booking.objects.filter(booking_status='completed').count()
        context['total_users'] = CustomUser.objects.filter(role='user').count()
        context['total_earning'] = Booking.objects.filter(booking_status='completed').aggregate(
            total=models.Sum('final_total')
        )['total'] or 0
        context['total_rental'] = Booking.objects.filter(shop_type__isnull=False).count()

        return context
