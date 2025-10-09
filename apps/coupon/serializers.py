from rest_framework import serializers
from .models import Coupon
from apps.auths.models import CustomUser

class CouponSerializer(serializers.ModelSerializer):
    is_expired = serializers.SerializerMethodField()
    remaining_uses = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['code', 'created_at', 'updated_at']

    def get_is_expired(self, obj):
        return obj.is_expired()

    def get_remaining_uses(self, obj):
        return obj.remaining_uses()


class CouponMultiEmailSerializer(serializers.Serializer):
    coupon_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    email = serializers.EmailField(
        allow_blank=False
    )



class UserEmailSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email']