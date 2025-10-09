from .models import Coupon
from .serializers import CouponSerializer
from ..core.crud import DynamicModelViewSet
from ..core.pagination import CustomPagination
from ..core.permissions import IsAdminRole
from ..core.publicApi import BasePublicAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from apps.auths.models import CustomUser
from .models import Coupon
from .serializers import CouponMultiEmailSerializer, UserEmailSearchSerializer
from apps.core.response import failure_response, success_response



class CouponViewSet(DynamicModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        kwargs['model'] = Coupon
        kwargs['serializer_class'] = CouponSerializer
        kwargs['item_name'] = 'Coupon'
        super().__init__(*args, **kwargs)


class UserSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.GET.get("q", "")
        users = CustomUser.objects.filter(email__icontains=query)[:10]
        serializer = UserEmailSearchSerializer(users, many=True)
        return success_response("User Retrive Successfully!",serializer.data)


class SendMultipleCouponsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CouponMultiEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon_ids = [int(c) for c in serializer.validated_data['coupon_ids']]
        email = serializer.validated_data['email']
        print(coupon_ids)
        coupons = Coupon.objects.filter(id__in=coupon_ids)
        if not coupons.exists():
            return failure_response({"error": "No valid coupons found."}, status=status.HTTP_404_NOT_FOUND)

        user = CustomUser.objects.filter(email=email)
        print(coupons)
        
        if not user.exists():
            return failure_response("No valid user found...", status=status.HTTP_400_BAD_REQUEST)

        subject = "🎁 Special Discount Coupons Just for You!"
        coupon_list = "\n".join([f"- {c.name} ({c.code}) — Expires {c.expiry_date}" for c in coupons])
        message = f"""
                Hello!

                You have received special discount coupons:

                {coupon_list}

                Enjoy your shopping!

                — Your Company Team
                """
        from_email = "noreply@yourdomain.com"
        recipient_list = [u.email for u in user if u.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        return success_response(
            message= f"Sent {len(coupons)} coupons to {len(recipient_list)} users.",
            data={ "sent_coupons": [c.code for c in coupons]}
        )

