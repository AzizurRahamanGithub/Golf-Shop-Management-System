from django.contrib import admin
from .models import Category, Feature, Package, Shop, Review
from .forms import SingleImageForm, MultipleImagesForm

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = type(
        'CategorySingleImageForm',
        (SingleImageForm,),
        {
            'Meta': type('Meta', (SingleImageForm.Meta,), {'model': Category}),
            'image_folder': 'category'
        }
    )
    list_display = ( "name", "created_at", "updated_at")
    fieldsets = (
        ('Basic Info', {
            'fields': ('name',)
        }),
        ('Image', {
            'fields': ('upload_image',)  # show custom image field
        })
    )
    search_fields = ("name",)
    ordering = ("-created_at",)
    list_per_page = 10
    
    def get_model_perms(self, request):
        """Show under 'CategoryAdmin' instead of default name."""
        perms = super().get_model_perms(request)
        perms['name'] = 'Customer Reviews'
        return perms


class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    # Use multiple images form
    form = type(
        'PackageMultipleImagesForm',
        (MultipleImagesForm,),
        {
            'Meta': type('Meta', (MultipleImagesForm.Meta,), {'model': Package}),
            'image_folder': 'packages'
        }
    )
    list_display = ("name", "price", "stock", "created_at", "updated_at")
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'price', 'description', 'stock')
        }),
        ('Images', {
            'fields': ('upload_images',)  # custom multiple images preview
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description")
    inlines = [FeatureInline]
    ordering = ("-created_at",)
    list_per_page = 10
    readonly_fields = ("created_at", "updated_at")
    
    def get_model_perms(self, request):
        """Show under 'PackageAdmin' instead of default name."""
        perms = super().get_model_perms(request)
        perms['name'] = 'Package Items'
        return perms


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    # Use multiple images form
    form = type(
        'ShopMultipleImagesForm',
        (MultipleImagesForm,),
        {
            'Meta': type('Meta', (MultipleImagesForm.Meta,), {'model': Shop}),
            'image_folder': 'shop'
        }
    )
    list_display = ("name", "category", "price", "is_active", "publish_date", "stock")
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'price', 'is_active', 'publish_date', 'stock', 'description')
        }),
        ('Images', {
            'fields': ('upload_images',)  # show the custom preview/upload field
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
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
