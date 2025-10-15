from django.contrib import admin, messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from .models import Coupon, CouponEmailLog
from apps.auths.models import CustomUser

# Simple email form for confirmation
class SendCouponEmailForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    email = forms.EmailField(label="Recipient Email")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'discount_type',
        'discount_value',
        'expiry_date',
        'usage_limit',
        'used_count',
        'is_active',
        'created_at',
    )
    list_filter = ('discount_type', 'is_active', 'expiry_date')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('code', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    actions = ['send_coupons_to_email']

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "description", "discount_type", "discount_value")
        }),
        ("Usage & Status", {
            "fields": ("usage_limit", "used_count", "is_active")
        }),
        ("Code & Dates", {
            "fields": ("code", "expiry_date", "created_at", "updated_at")
        }),
    )

# ==================================
#  CouponEmailLog — auto email send
# ==================================



@admin.register(CouponEmailLog)
class CouponEmailLogAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'sent_at')
    search_fields = ('coupon__code',)
    list_filter = ('sent_at',)
    filter_horizontal = ('recipients',)

    def save_model(self, request, obj, form, change):
        # just save the object first
        super().save_model(request, obj, form, change)
        # don't send email here, because recipients aren't saved yet

    def save_related(self, request, form, formsets, change):
        """
        Called after ManyToMany fields are saved.
        This is the correct place to send the email.
        """
        super().save_related(request, form, formsets, change)
        obj = form.instance  # the saved CouponEmailLog

        recipients = obj.recipients.all()
        if not recipients:
            self.message_user(request, "⚠️ No recipients selected. Email not sent.", level=messages.WARNING)
            return

        subject = "🎁 You've received a new discount coupon!"
        message = f"""
        Hello,

        You've received a special coupon:

        - {obj.coupon.name} ({obj.coupon.code})
        - Expires: {obj.coupon.expiry_date}

        Enjoy your shopping!

        — Your Company Team
        """
        from_email = "noreply@yourdomain.com"
        recipient_list = [user.email for user in recipients if user.email]

        if recipient_list:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            self.message_user(
                request,
                f"✅ Coupon '{obj.coupon.code}' sent to {len(recipient_list)} user(s).",
                level=messages.SUCCESS,
            )
        else:
            self.message_user(request, "⚠️ No valid email addresses found.", level=messages.WARNING)
