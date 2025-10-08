from rest_framework import serializers
from .models import Booking
from apps.cart.models import Cart
from apps.products.models import Shop,Package
from apps.products.serializers import ShopSerializer, PackageSerializer

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["user", "created_at", "shop", "package", "total_price"]

    def validate(self, data):
        cart = self.context.get('cart')
        if not cart:
            user = self.context['request'].user
            cart = Cart.objects.filter(user=user).order_by('-created_at').first()

        if not cart:
            raise serializers.ValidationError("Cart does not exist.")
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")

        total_price = 0
        shop_ids = []
        package_ids = []

        for item in cart.items.all():
            total_price += item.total_price()
            if item.shop:
                shop_ids.append(item.shop.id)
            if item.package:
                package_ids.append(item.package.id)

        data["shops"] = shop_ids
        data["packages"] = package_ids
        data["shop"] = Shop.objects.filter(id=shop_ids[0]).first() if shop_ids else None
        data["package"] = Package.objects.filter(id=package_ids[0]).first() if package_ids else None
        data["total_price"] = total_price

        return data

    def create(self, validated_data):
        return super().create(validated_data)


class BookingHistorySerializer(serializers.ModelSerializer):
    shops = serializers.SerializerMethodField()
    packages = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ["shops", "packages"]

    def get_shops(self, obj):
        shop_ids = obj.shops or []
        shops = Shop.objects.filter(id__in=shop_ids)
        return ShopSerializer(shops, many=True).data

    def get_packages(self, obj):
        package_ids = obj.packages or []
        packages = Package.objects.filter(id__in=package_ids)
        return PackageSerializer(packages, many=True).data
