from rest_framework import serializers
from .models import Category, Feature, Package, Shop


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = "__all__"


class PackageSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)  
    feature_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Feature.objects.all(), source="features"
    )

    class Meta:
        model = Package
        fields = ["id", "name", "price", "images", "description", "features", "feature_ids", "created_at", "updated_at"]


class ShopSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Category.objects.all(), source="category"
    )

    class Meta:
        model = Shop
        fields = ["id", "name", "description", "category", "category_id", "is_active", "price", "publish_date", "images", "created_at", "updated_at"]
