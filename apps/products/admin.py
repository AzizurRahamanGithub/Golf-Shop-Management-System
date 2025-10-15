from django.contrib import admin
from .models import Category, Feature, Package, Shop, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ( "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
    list_per_page = 25
    
    # def get_model_perms(self, request):
    #     """Show under 'CategoryAdmin' instead of default name."""
    #     perms = super().get_model_perms(request)
    #     perms['name'] = 'Customer Reviews'
    #     return perms


class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description")
    inlines = [FeatureInline]
    ordering = ("-created_at",)
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")
    
    def get_model_perms(self, request):
        """Show under 'PackageAdmin' instead of default name."""
        perms = super().get_model_perms(request)
        perms['name'] = 'Package Items'
        return perms


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "publish_date", "stock")
    list_filter = ("is_active", "category", "publish_date")
    search_fields = ("name", "description")
    ordering = ("-publish_date",)
    list_editable = ("is_active",)
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")
    
    def get_model_perms(self, request):
        """Show under 'ShopAdmin' instead of default name."""
        perms = super().get_model_perms(request)
        perms['name'] = 'Shop Items'
        return perms


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ( "user", "shop", "package", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__email", "shop__name", "package__name", "comment")
    ordering = ("-created_at",)
    list_per_page = 25


    def get_model_perms(self, request):
        """Show under 'Customer Reviews' instead of default name."""
        perms = super().get_model_perms(request)
        perms['name'] = 'Customer Reviews'
        return perms
