from rest_framework import serializers
from .models import Booking
from apps.cart.models import Cart

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["user", "created_at", "shop", "package", "total_price"]

    def validate(self, data):
        cart = self.context.get('cart')
        if not cart:
            if 'request' not in self.context:
                raise serializers.ValidationError("Request context is missing.")
            
            user = self.context['request'].user
            cart = Cart.objects.filter(user=user).order_by('-created_at').first()
        
        if not cart:
            raise serializers.ValidationError("Cart does not exist.")

        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")

        total_price = 0
        shops = []
        packages = []

        # Iterate over the cart items
        for item in cart.items.all():
            total_price += item.total_price()

            # Collect all shops and packages
            if item.shop:
                shops.append(item.shop)
            if item.package:
                packages.append(item.package)

        # Decide which shop/package to associate with booking
        # Option 1: Use the first one found
        data['shop'] = shops[0] if shops else None
        data['package'] = packages[0] if packages else None

        data['total_price'] = total_price

        return data

    def create(self, validated_data):
        return super().create(validated_data)