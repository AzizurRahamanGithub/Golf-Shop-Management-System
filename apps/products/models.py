from django.db import models
from django.utils import timezone
import random
from datetime import timedelta
from django.conf import settings

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name