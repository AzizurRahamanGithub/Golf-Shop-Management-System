import string
import random
from django.db import models
from django.utils import timezone
from apps.auths.models import CustomUser


from django.db import models
from django.utils.html import strip_tags

class EmailCategory(models.TextChoices):
    PROMOTION = 'promotion', 'Promotion'
    COUPON = 'coupon', 'Coupon'
    EVENT = 'event', 'Event'
    REMINDER = 'reminder', 'Reminder'
    CUSTOM = 'custom', 'Custom'


# models.py (snippet)
class EmailTemplate(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=EmailCategory.choices, default=EmailCategory.CUSTOM)
    subject = models.CharField(max_length=255)
    body_html = models.TextField()
    body_text = models.TextField(blank=True, null=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        from django.utils.html import strip_tags
        self.body_text = strip_tags(self.body_html or "")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class DiscountType(models.TextChoices):
    PERCENTAGE = 'percentage', 'Percentage'
    FIXED = 'fixed', 'Fixed Amount'


def generate_unique_code():
    from .models import Coupon  # local import to avoid circular issue
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Coupon.objects.filter(code=code).exists():
            return code


class Coupon(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, editable=False)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:  # only generate on first creation
            self.code = generate_unique_code()
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now().date() > self.expiry_date

    def remaining_uses(self):
        return max(self.usage_limit - self.used_count, 0)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['-created_at']


class CouponEmailLog(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="email_logs")
    template = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    recipients = models.ManyToManyField(CustomUser, related_name="coupon_emails")
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Coupon '{self.coupon.code}' sent on {self.sent_at}"
