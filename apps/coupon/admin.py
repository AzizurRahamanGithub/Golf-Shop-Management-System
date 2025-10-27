# apps/coupon/admin.py
from django.contrib import admin, messages
from django.core.mail import send_mail
from django import forms
from django.template import Template, Context
from tinymce.widgets import TinyMCE

from .models import Coupon, CouponEmailLog, EmailTemplate
from apps.auths.models import CustomUser

# -------------------------
# Coupon Admin
# -------------------------
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "discount_type", "discount_value", "expiry_date", "is_active", "created_at")
    list_filter = ("discount_type", "is_active", "expiry_date")
    search_fields = ("name", "code", "description")
    readonly_fields = ("code", "created_at", "updated_at")
    ordering = ("-created_at",)
    fieldsets = (
        ("Basic Info", {"fields": ("name", "description", "discount_type", "discount_value")}),
        ("Usage & Status", {"fields": ("usage_limit", "used_count", "is_active")}),
        ("Code & Dates", {"fields": ("code", "expiry_date", "created_at", "updated_at")}),
    )

# -------------------------
# CouponEmailLog Admin
# -------------------------
# apps/coupon/admin.py (only the admin for CouponEmailLog)
from django.contrib import admin, messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import Template, Context
from .models import CouponEmailLog

@admin.register(CouponEmailLog)
class CouponEmailLogAdmin(admin.ModelAdmin):
    list_display = ("coupon", "template", "sent_at")
    search_fields = ("coupon__code",)
    list_filter = ("sent_at", "template")
    filter_horizontal = ("recipients",)

    fieldsets = (
        (None, {"fields": ("coupon", "template", "recipients")}),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance
        recipients = list(obj.recipients.all())

        # quick debug:
        print("=== EMAIL LOG EXECUTION ===")
        print("DEFAULT_FROM_EMAIL:", settings.DEFAULT_FROM_EMAIL)
        print("RECIPIENTS:", [getattr(u, "email", None) for u in recipients])

        if not recipients:
            self.message_user(
                request,
                "⚠️ No recipients selected. Email not sent.",
                level=messages.WARNING
            )
            return

        coupon = obj.coupon
        coupons = [coupon]

        sent_count = 0
        fail_count = 0

        with get_connection() as conn:
            for user in recipients:
                to_email = getattr(user, "email", None)
                if not to_email:
                    continue

                ctx = {
                    "user": user,
                    "coupon": coupon,
                    "coupons": coupons,
                }

                # Safe template rendering
                if obj.template:
                    raw_subject = obj.template.subject or ""
                    raw_html = obj.template.body_html or ""
                    raw_text = obj.template.body_text or ""

                    subject = Template(raw_subject).render(Context(ctx))
                    html_body = Template(raw_html).render(Context(ctx))
                    text_body = Template(raw_text).render(Context(ctx))
                else:
                    subject = "🎁 You've received a new discount coupon!"
                    text_body = (
                        f"Hello {getattr(user, 'first_name', '') or ''}\n\n"
                        f"You've received a special coupon:\n\n"
                        f"- {coupon.name} ({coupon.code})\n"
                        f"- Expires: {coupon.expiry_date}\n\n"
                        "Enjoy your shopping!\n— Your Company Team"
                    )
                    html_body = f"""
                        <p>Hello {getattr(user, 'first_name', '') or ''},</p>
                        <p>You've received a special coupon:</p>
                        <ul>
                            <li>{coupon.name} ({coupon.code})</li>
                            <li>Expires: {coupon.expiry_date}</li>
                        </ul>
                        <p>Enjoy your shopping!<br>— Your Company Team</p>
                    """

                try:
                    # USE VERIFIED SENDER HERE
                    msg = EmailMultiAlternatives(
                        subject,
                        text_body,
                        settings.DEFAULT_FROM_EMAIL,  # << critical
                        [to_email],
                        connection=conn
                    )
                    msg.attach_alternative(html_body, "text/html")
                    result = msg.send(fail_silently=False)

                    print("SENT TO:", to_email, "RESULT:", result)
                    sent_count += 1
                except Exception as e:
                    print("FAILED TO SEND TO:", to_email)
                    print(e)
                    fail_count += 1

        if fail_count == 0:
            self.message_user(
                request,
                f"✅ Email attempted to {sent_count} recipient(s).",
                level=messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                f"❌ Sent {sent_count}, failed {fail_count}. Check runserver console for details.",
                level=messages.ERROR,
            )


# -------------------------
# EmailTemplate Admin (TinyMCE)
# -------------------------
class EmailTemplateAdminForm(forms.ModelForm):
    subject = forms.CharField(
        widget=forms.TextInput(attrs={"style": "width:90%;"}),
        help_text="Placeholders: {{ user.first_name }}, {{ coupon.code }}, etc."
    )
    body_html = forms.CharField(
        widget=TinyMCE(attrs={"cols": 80, "rows": 25}),
        help_text="Write HTML. Supports Django template tags/variables."
    )

    class Meta:
        model = EmailTemplate
        # IMPORTANT: exclude the non-editable field to avoid FieldError
        exclude = ("body_text",)   # <— this fixes your error

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateAdminForm
    list_display = ("name", "category", "is_active", "created_at", "updated_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "subject", "body_html")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "body_text")  # show generated plain text
    fieldsets = (
        ("Template Info", {"fields": ("name", "category", "is_active")}),
        ("Email Content", {"fields": ("subject", "body_html", "body_text")}),  # body_text is readonly → OK
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    # Optional: quick preview with sample context
    def response_change(self, request, obj):
        if "_preview" in request.POST:
            from django.http import HttpResponse
            sample_user = CustomUser(email="sample@demo.com", first_name="Sample", last_name="User")
            sample_coupon = Coupon(name="New Year Deal", code="ABC123", expiry_date="2099-12-31")
            ctx = {"user": sample_user, "coupon": sample_coupon, "coupons": [sample_coupon]}
            subject = Template(obj.subject).render(Context(ctx))
            html = Template(obj.body_html).render(Context(ctx))
            return HttpResponse(f"""
<!doctype html><html><head><meta charset="utf-8"><title>Preview: {subject}</title></head>
<body style="padding:24px;max-width:800px;margin:0 auto;background:#f7f7f7;">
  <div style="background:#fff;padding:24px;border:1px solid #e5e5e5;">
    <h2 style="margin-top:0;">Subject: {subject}</h2><hr>{html}
  </div>
</body></html>
""")
        return super().response_change(request, obj)
