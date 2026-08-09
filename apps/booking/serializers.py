# apps/booking/serializers.py
from django.db.models import Q
from decimal import Decimal
from datetime import datetime
from rest_framework import serializers
from .models import Booking, Coupon, Shop, Package
from apps.products.serializers import ShopSerializer, PackageSerializer

def extract_ids(data, single_key, list_key):
    ids = []
    # Try getting from list first
    list_val = data.get(list_key)
    if isinstance(list_val, list):
        for x in list_val:
            try:
                if x:
                    ids.append(int(x))
            except (ValueError, TypeError):
                pass
    # Try getting from single value
    single_val = data.get(single_key)
    if single_val:
        if hasattr(single_val, 'id'):
            ids.append(single_val.id)
        else:
            try:
                ids.append(int(single_val))
            except (ValueError, TypeError):
                pass
    return list(set(ids))

def validate_booking_duration_and_overlap(start_date, end_date, start_time, end_time, shop_ids, package_ids, exclude_booking_id=None):
    # Enforce Maximum 4-Hour Duration Check
    if not end_date:
        end_date = start_date
        
    start_dt = datetime.combine(start_date, start_time)
    end_dt = datetime.combine(end_date, end_time)
    
    if end_dt <= start_dt:
        raise serializers.ValidationError("End date/time must be after start date/time.")
        
    duration = end_dt - start_dt
    if duration.total_seconds() > 4 * 3600:
        raise serializers.ValidationError("Booking duration cannot exceed a maximum of 4 hours.")
        
    # Ensure at least one shop or package is selected - Removed as requested
    pass

    # Strict Overlap Prevention for the selected shops and packages
    # Find all bookings that overlap in terms of date/time
    overlapping_bookings = Booking.objects.filter(
        start_date__lte=end_date,
        end_date__gte=start_date,
        start_time__lt=end_time,
        end_time__gt=start_time
    )
    
    if exclude_booking_id:
        overlapping_bookings = overlapping_bookings.exclude(id=exclude_booking_id)
        
    for b in overlapping_bookings:
        # Collect shop IDs in the existing booking
        existing_shop_ids = set()
        if b.shop_id:
            existing_shop_ids.add(b.shop_id)
        if b.shops:
            existing_shop_ids.update(b.shops)
            
        common_shops = existing_shop_ids.intersection(shop_ids)
        if common_shops:
            overlapping_shop_names = list(Shop.objects.filter(id__in=common_shops).values_list('name', flat=True))
            shop_str = ", ".join(overlapping_shop_names) if overlapping_shop_names else "selected shop"
            raise serializers.ValidationError(
                f"The following shop(s) are already booked during this time: {shop_str}. Please choose another time slot."
            )
            
        # Collect package IDs in the existing booking
        existing_package_ids = set()
        if b.package_id:
            existing_package_ids.add(b.package_id)
        if b.packages:
            existing_package_ids.update(b.packages)
            
        common_packages = existing_package_ids.intersection(package_ids)
        if common_packages:
            overlapping_package_names = list(Package.objects.filter(id__in=common_packages).values_list('name', flat=True))
            package_str = ", ".join(overlapping_package_names) if overlapping_package_names else "selected package"
            raise serializers.ValidationError(
                f"The following package(s) are already booked during this time: {package_str}. Please choose another time slot."
            )


class BookingValidationSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)
    
    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        
        # Extract shop and package IDs directly from request
        shop_ids = extract_ids(self.initial_data, "shop", "shops")
        package_ids = extract_ids(self.initial_data, "package", "packages")
        
        validate_booking_duration_and_overlap(
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            shop_ids=shop_ids,
            package_ids=package_ids
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
        # Extract shop and package IDs from request (checks both data and initial_data)
        shop_ids = extract_ids(data, "shop", "shops")
        if not shop_ids:
            shop_ids = extract_ids(self.initial_data, "shop", "shops")

        package_ids = extract_ids(data, "package", "packages")
        if not package_ids:
            package_ids = extract_ids(self.initial_data, "package", "packages")

        start_date = data.get("start_date")
        end_date = data.get("end_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        exclude_id = self.instance.id if self.instance else None

        validate_booking_duration_and_overlap(
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            shop_ids=shop_ids,
            package_ids=package_ids,
            exclude_booking_id=exclude_id
        )

        # Secure total price calculation using database
        total_price = Decimal('0.00')
        if shop_ids:
            shops_qs = Shop.objects.filter(id__in=shop_ids)
            total_price += sum(shop.price for shop in shops_qs)
        if package_ids:
            packages_qs = Package.objects.filter(id__in=package_ids)
            total_price += sum(package.price for package in packages_qs)

        tax = (total_price * Decimal('0.05')).quantize(Decimal('0.01'))

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

            if coupon.discount_type == 'percentage':
                discount_amount = (total_price * (coupon.discount_value / Decimal('100'))).quantize(Decimal('0.01'))
            elif coupon.discount_type == 'fixed':
                discount_amount = Decimal(coupon.discount_value).quantize(Decimal('0.01'))

        if discount_amount > total_price:
            discount_amount = total_price

        final_total = (total_price + tax - discount_amount).quantize(Decimal('0.01'))

        shop = Shop.objects.filter(id__in=shop_ids).first() if shop_ids else None
        package = Package.objects.filter(id__in=package_ids).first() if package_ids else None

        data.update({
            "shops": shop_ids,
            "packages": package_ids,
            "shop": shop,
            "package": package,
            "total_price": total_price,
            "tax": tax,
            "discount_amount": discount_amount,
            "final_total": final_total,
        })

        self._coupon_instance = coupon
        return data

    def create(self, validated_data):
        validated_data.pop("coupon_code", None)
        booking = super().create(validated_data)

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