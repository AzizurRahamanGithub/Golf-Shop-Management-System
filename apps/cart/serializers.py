from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ShopSerializer, PackageSerializer
from apps.products.models import Shop, Package


class CartItemSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    package = PackageSerializer(read_only=True)

    shop_id = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), source="shop", write_only=True, required=False
    )
    package_id = serializers.PrimaryKeyRelatedField(
        queryset=Package.objects.all(), source="package", write_only=True, required=False
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "shop",
            "package",
            "shop_id",
            "package_id",
            "quantity",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.total_price()

    def validate(self, data):
        # must have either shop or package
        if not data.get("shop") and not data.get("package"):
            raise serializers.ValidationError("Either shop_id or package_id is required.")
        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total"]
        read_only_fields = ["user"]

    def get_total(self, obj):
        return obj.total_price()