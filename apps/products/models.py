from django.db import models
from django.utils import timezone
import random
from datetime import timedelta
from django.conf import settings
from apps.auths.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Feature(models.Model):
    package = models.ForeignKey("Package", on_delete=models.CASCADE, related_name="features")
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.package.name})"


class Package(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    images = models.JSONField(null=True, blank=True)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Package"
        verbose_name_plural = "Packages"

    def __str__(self):
        return self.name



class Shop(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="shops")
    is_active = models.BooleanField(default=False)
    price = models.IntegerField()
    publish_date = models.DateField()
    images = models.JSONField(null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reviews")
    shop = models.ForeignKey("Shop", on_delete=models.CASCADE, null=True, blank=True, related_name="reviews")
    package = models.ForeignKey("Package", on_delete=models.CASCADE, null=True, blank=True, related_name="reviews")

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]

    def __str__(self):
        target = self.shop.name if self.shop else self.package.name if self.package else "Unknown"
        return f"{self.user} - {target} ({self.rating}★)"