from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.utils.html import format_html
from .models import Blog
from .forms import UploadAdminForm

@admin.register(Blog)
class BlogAdmin(SummernoteModelAdmin):
    form = UploadAdminForm
    list_display = ("title","colored_status", "created_at")
    list_filter = ("blog_status", "created_at")
    search_fields = ("title", "description")
    summernote_fields = ('description',)

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Blog Details", {
            "fields": (
                "title","description",             # first row
                ("upload_image", "image"), 
                ("delete_image", "blog_status", "created_at"),
                
            )
        }),
    )
    
    def colored_status(self, obj):
        color_map = {
            "published": "#0D9125",  # তোমার দেওয়া primary green
            "pending": "#f59e0b",    # orange
            "failed": "#ef4444",     # red
        }
        color = color_map.get(obj.blog_status.lower(), "#6b7280")  # default gray
        return format_html(
            '<span style="color: white; background-color: {}; padding: 4px 10px; '
            'border-radius: 6px; font-size: 12px; font-weight: 500; text-transform: capitalize; '
            'box-shadow: 0 0 6px {}80;">{}</span>',
            color,
            color,
            obj.blog_status
        )

    colored_status.short_description = "Blog status"

    class Media:
        css = {
            "all": ("css/custom_admin.css",)
        }
