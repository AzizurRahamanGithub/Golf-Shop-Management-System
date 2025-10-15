
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin
from apps.booking.models import Booking, Payment
from apps.auths.models import CustomUser
from django.db.models import Sum

from .models import DashboardDummy

class AdminDashboardView(UnfoldModelAdminViewMixin, TemplateView):
    template_name = "dashboard.html"
    title = "Admin Dashboard"
    permission_required = ()  # no permission restrictions for now

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Total bookings with completed status
        context['total_bookings'] = Booking.objects.filter(booking_status='completed').count()

        # Total users with role = user
        context['total_users'] = CustomUser.objects.filter(role='user').count()

        # Total earning (sum of final_total for completed bookings)
        context['total_earning'] = Booking.objects.filter(booking_status='completed').aggregate(
            total=Sum('final_total')
        )['total'] or 0

        # Total rentals (bookings with non-null shop_type)
        context['total_rental'] = Booking.objects.filter(shop_type__isnull=False).count()

        return context

@admin.register(DashboardDummy)
class DashboardDummyAdmin(admin.ModelAdmin):
    def get_urls(self):
        custom_view = self.admin_site.admin_view(
            AdminDashboardView.as_view(model_admin=self)
        )

        urls = super().get_urls()
        return [
            path("", custom_view, name="admin_dashboard"),
        ] + urls
