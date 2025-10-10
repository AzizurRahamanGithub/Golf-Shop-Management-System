# apps/booking/serializers.py

from decimal import Decimal
from rest_framework import serializers
from .models import Booking
from apps.cart.models import Cart
from apps.products.models import Shop, Package
from apps.products.serializers import ShopSerializer, PackageSerializer
from apps.coupon.models import Coupon


class BookingSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tax_amount = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = [
            "user",
            "created_at",
            "shop",
            "package",
            "total_price",
            "final_total",
            "discount_amount",
            "tax",
        ]

    def get_tax_amount(self, obj):
        """Show 5% tax value in response"""
        return round(obj.tax, 2) if obj.tax else 0

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        cart = Cart.objects.filter(user=user).order_by('-created_at').first()

        if not cart:
            raise serializers.ValidationError("Cart does not exist.")
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")

        # Step 1: Calculate subtotal
        total_price = Decimal(sum(item.total_price() for item in cart.items.all()))

        # Step 2: Add 5% tax
        tax = (total_price * Decimal('0.05')).quantize(Decimal('0.01'))

        # Step 3: Check and apply coupon
        coupon_code = self.initial_data.get("coupon_code", "").strip()
        coupon = None
        discount_amount = Decimal('0.00')

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Invalid coupon code.")

            if coupon.is_expired():
                raise serializers.ValidationError("This coupon has expired.")
            if coupon.remaining_uses() <= 0:
                raise serializers.ValidationError("Coupon usage limit reached.")

            # Apply discount based on type
            if coupon.discount_type == 'percentage':
                discount_amount = (total_price * (coupon.discount_value / Decimal('100'))).quantize(Decimal('0.01'))
            elif coupon.discount_type == 'fixed':
                discount_amount = Decimal(coupon.discount_value).quantize(Decimal('0.01'))

        # Step 4: Prevent over-discount
        if discount_amount > total_price:
            discount_amount = total_price

        # Step 5: Calculate final total
        final_total = (total_price + tax - discount_amount).quantize(Decimal('0.01'))

        # Step 6: Collect related data
        shop_ids = [i.shop.id for i in cart.items.all() if i.shop]
        package_ids = [i.package.id for i in cart.items.all() if i.package]

        # Store values in validated_data (only model fields)
        data.update({
            "shops": shop_ids,
            "packages": package_ids,
            "shop": Shop.objects.filter(id__in=shop_ids).first() if shop_ids else None,
            "package": Package.objects.filter(id__in=package_ids).first() if package_ids else None,
            "total_price": total_price,
            "tax": tax,
            "discount_amount": discount_amount,
            "final_total": final_total,
        })

        # Store coupon separately (not part of Booking model)
        self._coupon_instance = coupon

        return data

    def create(self, validated_data):
        # Remove coupon_code (not a model field)
        validated_data.pop("coupon_code", None)

        # Create the booking
        booking = super().create(validated_data)

        # Handle coupon usage safely
        coupon = getattr(self, "_coupon_instance", None)
        if coupon:
            coupon.used_count += 1
            coupon.save()

        return booking



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