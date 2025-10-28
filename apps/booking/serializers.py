# apps/booking/serializers.py
from django.db.models import Q
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

from django.db.models import Q
from decimal import Decimal

class BookingValidationSerializer(serializers.Serializer):
    
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)  # Add end_date validation
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)
    
    def validate(self, data):
        # Retrieve start_date, end_date, start_time, and end_time from the request data
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        
        # Retrieve shop and package IDs (if needed for further checks, can be omitted)
        shop_ids = self.context.get('shop_ids', [])
        package_ids = self.context.get('package_ids', [])

        # ==============================
        # 🧠 Booking Time Conflict Check
        # ==============================
        # We need to consider both the start date and the end date
        overlapping = Booking.objects.filter(
            start_date__lte=end_date,  # Check if the booking starts before or on the requested end date
            end_date__gte=start_date,  # Check if the booking ends after or on the requested start date
            start_time__lt=end_time,   # Check if the booking's start time is before the requested end time
            end_time__gt=start_time    # Check if the booking's end time is after the requested start time
        )
        
        # Handle shop filtering only if shop_ids are provided (non-empty list)
        if shop_ids:
            overlapping = overlapping.filter(shop__id__in=shop_ids)
        
        # Handle package filtering only if package_ids are provided (non-empty list)
        if package_ids:
            overlapping = overlapping.filter(package__id__in=package_ids)

        # If any overlap exists, raise an error
        if overlapping.exists():
            raise serializers.ValidationError(
                "This time range is already booked for the selected shop/package. Please choose another time slot."
            )
        return data



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

        # ==============================
        # Shop and Package Validation
        # ==============================
        shop_ids = [i.shop.id for i in cart.items.all() if i.shop]
        package_ids = [i.package.id for i in cart.items.all() if i.package]

        # Ensure at least one shop or package is selected
        if not shop_ids and not package_ids:
            raise serializers.ValidationError("At least one shop or package must be selected.")

        # ==============================
        # 🧠 Booking Time Conflict Check
        # ==============================
        start_date = data.get("start_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        overlapping = Booking.objects.filter(
            start_date=start_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        shop = None  # Default to None to handle cases where no shop is selected
        package = None  # Default to None to handle cases where no package is selected

        # Handle shop overlapping
        if shop_ids:
            shop = Shop.objects.filter(id__in=shop_ids).first()
            if not shop:
                raise serializers.ValidationError("No valid shop found for booking.")
            overlapping = overlapping.filter(shop=shop)

        # Handle package overlapping
        if package_ids:
            # For package, check for overlap using the package_ids
            overlapping = overlapping.filter(Q(packages__in=package_ids))

        # Exclude current booking if updating
        if self.instance:
            overlapping = overlapping.exclude(id=self.instance.id)

        # If any overlap exists, raise an error
        if overlapping.exists():
            raise serializers.ValidationError(
                "This shop/package is already booked during the selected time range. Please choose another time slot."
            )

        # ==============================
        # 💰 Price, Tax & Coupon Logic
        # ==============================
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

            # Apply discount based on coupon type
            if coupon.discount_type == 'percentage':
                discount_amount = (total_price * (coupon.discount_value / Decimal('100'))).quantize(Decimal('0.01'))
            elif coupon.discount_type == 'fixed':
                discount_amount = Decimal(coupon.discount_value).quantize(Decimal('0.01'))

        # Prevent over-discount
        if discount_amount > total_price:
            discount_amount = total_price

        # Calculate final total
        final_total = (total_price + tax - discount_amount).quantize(Decimal('0.01'))

        # Store calculated values in data
        data.update({
            "shops": shop_ids,
            "packages": package_ids,
            "shop": shop,
            "package": Package.objects.filter(id__in=package_ids).first() if package_ids else None,
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
        fields = [
            "id",
            "user",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "total_price",
            "tax",
            "final_total",
            "discount_amount",
            "shop",
            "package",
            "shops",
            "packages",
            "created_at",
            "booking_status",
            "number_of_guests",
            "full_name",
            "email",
            "phone",
            "street_address",
            "city",
            "zip_code",
            "coupon",
            "damage_waiver",
            "signature",
            "signature_image",
            "payment_id"
        ]

    def get_shops(self, obj):
        # Retrieve the shops associated with the booking (using shop IDs from the booking)
        shop_ids = obj.shops or []
        shops = Shop.objects.filter(id__in=shop_ids)
        return ShopSerializer(shops, many=True).data

    def get_packages(self, obj):
        # Retrieve the packages associated with the booking (using package IDs from the booking)
        package_ids = obj.packages or []
        packages = Package.objects.filter(id__in=package_ids)
        return PackageSerializer(packages, many=True).data