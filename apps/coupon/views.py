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

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auths.models import CustomUser
from .models import Coupon, EmailTemplate, CouponEmailLog
from .serializers import (
    CouponSerializer, 
    CouponMultiEmailSerializer, 
    UserEmailSearchSerializer
)
from .email_workers import send_coupons_in_background
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
        return success_response("User Retrive Successfully!", serializer.data)


class SendMultipleCouponsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = CouponMultiEmailSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        coupon_ids = [int(c) for c in s.validated_data['coupon_ids']]
        email = s.validated_data['email']
        template_id = s.validated_data.get('template_id')

        coupons = list(Coupon.objects.filter(id__in=coupon_ids, is_active=True))
        if not coupons:
            return failure_response({"error": "No valid active coupons found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return failure_response("No valid user found...", status=status.HTTP_400_BAD_REQUEST)

        template = None
        if template_id:
            template = get_object_or_404(EmailTemplate, id=template_id, is_active=True)

        # Create a log row (optional)
        log = None
        with transaction.atomic():
            # if multiple coupons, you can log one row per coupon, or pick first
            log = CouponEmailLog.objects.create(
                coupon=coupons[0],  # or create multiple logs if needed
                template=template,
            )
            log.recipients.set([user])

            # start background sending AFTER commit
            transaction.on_commit(lambda: send_coupons_in_background(
                coupons=coupons,
                users=[user],
                template=template,
                from_email="noreply@yourdomain.com",
            ))

        return success_response(
            message=f"Email is being sent in the background to {user.email} (coupons: {len(coupons)}).",
            data={
                "log_id": log.id if log else None,
                "sent_coupons": [c.code for c in coupons],
                "template_used": template.name if template else "default"
            }
        )