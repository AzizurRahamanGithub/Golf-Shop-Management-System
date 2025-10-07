from rest_framework import serializers
from .models import Category, Feature, Package, Shop


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields= ['id', 'created_at', 'updated_at']


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id", "name", "created_at"]
        read_only_fields= ['id', "created_at"]


class PackageSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True)

    class Meta:
        model = Package
        fields = [
            "id",
            "name",
            "price",
            "images",
            "description",
            "features",
            "created_at",
            "updated_at",
        ]
        
        read_only_fields= ['id', 'updated_at', "created_at"]

    def create(self, validated_data):
        features_data = validated_data.pop("features", [])
        package = Package.objects.create(**validated_data)
        for feature in features_data:
            Feature.objects.create(package=package, **feature)
        return package



class ShopSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Category.objects.all(), source="category"
    )

    class Meta:
        model = Shop
        fields = ["id", "name", "description", "category", "category_id", "is_active", "price", "publish_date", "images", "created_at", "updated_at"]
        
        read_only_fields= ['id', 'created_at', "category_id", 'updated_at', "created_at"]
