from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Blog
from .forms import BlogAdminForm
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Blog)
class BlogAdmin(SummernoteModelAdmin):  # ✅ Only inherit from SummernoteModelAdmin
    form = BlogAdminForm
    list_display = ("title", "blog_status", "created_at")
    list_filter = ("blog_status", "created_at")
    search_fields = ("title", "description")
    summernote_fields = ('description',)

    class Media:
        css = {
            "all": ("css/custom_admin.css",)
        }
