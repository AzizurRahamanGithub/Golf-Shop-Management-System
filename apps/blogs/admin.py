from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Blog
from .forms import BlogAdminForm

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    list_display = ("title", "blog_status", "created_at")
    list_filter = ("blog_status", "created_at")
    search_fields = ("title", "description")

    class Media:
        css = {
            "all": ("css/custom_admin.css",)
        }

