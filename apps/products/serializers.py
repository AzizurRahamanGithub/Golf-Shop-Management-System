from rest_framework import serializers
from .models import Category, Feature, Package, Shop, Review
from django.db.models import Avg, Count
from apps.booking.models import Booking
from django.db.models import Q


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image", "created_at", "updated_at"]
        read_only_fields= ['id', 'created_at', 'updated_at']


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id", "name", "created_at"]
        read_only_fields= ['id', "created_at"]


class PackageSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    booked_count = serializers.SerializerMethodField()
    available_count = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            "id", "name", "price", "images", "description", "features",
            "created_at", "updated_at", "average_rating", "reviews_count",
            "booked_count", "available_count"
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        return obj.reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_booked_count(self, obj):
        return obj.bookings.count() if hasattr(obj, "bookings") else 0

    def get_available_count(self, obj):
        return obj.stock



class ShopSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Category.objects.all(), source="category"
    )
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    booked_count = serializers.SerializerMethodField()
    available_count = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_id",
            "is_active",
            "price",
            "publish_date",
            "images",
            "booked_count",
            "available_count",
            "created_at",
            "updated_at",
            "average_rating",
            "reviews_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_average_rating(self, obj):
        return obj.reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_booked_count(self, obj):
        # ✅ Universal method: works with any DB
        return obj.bookings.count() if hasattr(obj, "bookings") else 0

    def get_available_count(self, obj):
        return obj.stock

    
    
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    can_review = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "shop",
            "package",
            "rating",
            "comment",
            "created_at",
            "can_review",
        ]
        read_only_fields = ["user", "created_at", "can_review"]

    def validate(self, data):
        user = self.context["request"].user

        # Ensure at least one of shop/package exists
        if not data.get("shop") and not data.get("package"):
            raise serializers.ValidationError("Either shop or package must be provided.")

        # Prevent multiple reviews by the same user for same target
        if data.get("shop") and Review.objects.filter(user=user, shop=data["shop"]).exists():
            raise serializers.ValidationError("You have already reviewed this shop.")
        if data.get("package") and Review.objects.filter(user=user, package=data["package"]).exists():
            raise serializers.ValidationError("You have already reviewed this package.")

        return data

    def get_can_review(self, obj):
        user = self.context["request"].user

        # Get all completed bookings for the user
        bookings = Booking.objects.filter(user=user, booking_status="complete")

        # Check if this product (shop/package) exists in any booking
        for booking in bookings:
            if obj.shop and obj.shop.id in booking.shops:
                return True
            if obj.package and obj.package.id in booking.packages:
                return True
        return False


    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
