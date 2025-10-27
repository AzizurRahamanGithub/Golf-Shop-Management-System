# apps/booking/serializers.py

from decimal import Decimal
from rest_framework import serializers
from .models import Booking
from apps.cart.models import Cart
from apps.products.models import Shop, Package
from apps.products.serializers import ShopSerializer, PackageSerializer
from apps.coupon.models import Coupon


from rest_framework import serializers
from decimal import Decimal
from datetime import datetime
from .models import Booking, Coupon, Shop, Package
from apps.cart.models import Cart

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
            "discount_amount",
            "final_total",
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

        # =============================
        # 🧠 Booking Time Conflict Check
        # =============================
        start_date = data.get("start_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        # Get shop from cart (your flow uses Cart → Booking)
        shop_ids = [i.shop.id for i in cart.items.all() if i.shop]
        shop = Shop.objects.filter(id__in=shop_ids).first() if shop_ids else None

        if not shop:
            raise serializers.ValidationError("No valid shop found for booking.")

        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            shop=shop,
            start_date=start_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        # Exclude current booking if updating
        if self.instance:
            overlapping = overlapping.exclude(id=self.instance.id)

        if overlapping.exists():
            raise serializers.ValidationError(
                "This shop is already booked during the selected time range. Please choose another time slot."
            )

        # =============================
        # 💰 Price, Tax & Coupon Logic
        # =============================
        total_price = Decimal(sum(item.total_price() for item in cart.items.all()))

        # Add 5% tax
        tax = (total_price * Decimal('0.05')).quantize(Decimal('0.01'))

        # Coupon logic
        coupon_code = self.initial_data.get("coupon_code", "").strip()
        coupon = None
        discount_amount = Decimal('0.00')

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            except Coupon.DoesNotExist:
                raise serializers.ValidationError({"coupon_code": "Invalid coupon code."})

            if coupon.is_expired():
                raise serializers.ValidationError({"coupon_code": "This coupon has expired."})
            if coupon.remaining_uses() <= 0:
                raise serializers.ValidationError({"coupon_code": "Coupon usage limit reached."})

            # Apply discount
            if coupon.discount_type == 'percentage':
                discount_amount = (total_price * (coupon.discount_value / Decimal('100'))).quantize(Decimal('0.01'))
            elif coupon.discount_type == 'fixed':
                discount_amount = Decimal(coupon.discount_value).quantize(Decimal('0.01'))

        # Prevent over-discount
        if discount_amount > total_price:
            discount_amount = total_price

        # Calculate final total
        final_total = (total_price + tax - discount_amount).quantize(Decimal('0.01'))

        # Store calculated values
        data.update({
            "shops": shop_ids,
            "packages": [i.package.id for i in cart.items.all() if i.package],
            "shop": shop,
            "package": Package.objects.filter(id__in=[i.package.id for i in cart.items.all() if i.package]).first(),
            "total_price": total_price,
            "tax": tax,
            "discount_amount": discount_amount,
            "final_total": final_total,
        })

        self._coupon_instance = coupon
        return data

    def create(self, validated_data):
        # Remove coupon_code (not a model field)
        validated_data.pop("coupon_code", None)

        # Create booking
        booking = super().create(validated_data)

        # Update coupon usage
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