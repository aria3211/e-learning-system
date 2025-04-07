from datetime import timedelta
from urllib.parse import urljoin
from django.contrib.auth.hashers import make_password

from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status,generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from edue import settings
from .serializers import RegisterUserSerializer,UserLoginSerializer,ProfileSerializer,UserProfileSerializer,VerifyOtpSerializer
from accounts.models import User,OtpCode


class RegisterUserAPIView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            response_data = serializer.create(serializer.validated_data)
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")

        full_name = request.data.get("full_name")
        password = request.data.get("password")
        role = request.data.get("role")

        if not all([phone_number, otp, full_name, password, role]):
            return Response({"error": "همه‌ی فیلدها الزامی هستند."}, status=status.HTTP_400_BAD_REQUEST)

        otp_instance = get_object_or_404(OtpCode, phone_number=phone_number)

        if otp_instance.has_expired():
            otp_instance.delete()
            return Response({"error": "کد منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

        if int(otp_instance.max_otp_try) <= 0:
            otp_instance.delete()
            return Response({"error": "حداکثر تلاش انجام شده است."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_instance.otp != otp:
            otp_instance.max_otp_try = str(int(otp_instance.max_otp_try) - 1)
            otp_instance.save()
            return Response({"error": f"کد اشتباه است. {otp_instance.max_otp_try} تلاش باقی مانده."}, status=status.HTTP_400_BAD_REQUEST)

        # اگر کاربر وجود نداشت بسازش
        user = User.objects.create(
            phone_number=phone_number,
            full_name=full_name,
            role=role,
            password=make_password(password)
        )

        otp_instance.delete()

        return Response({"message": "ثبت‌نام با موفقیت انجام شد."}, status=status.HTTP_201_CREATED)
class GoogleLoginCallback(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")

        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        token_endpoint_url = urljoin("http://localhost:8000", reverse("google_login"))
        response = request.post(url=token_endpoint_url, data={"code": code})

        return Response(response.json(), status=status.HTTP_200_OK)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(role="STUDENT")

    def get_object(self):
        return self.request.user if self.request.user.role == "STUDENT" else None


class TeacherProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(role="TEACHER")

    def get_object(self):
        return self.request.user if self.request.user.role == "TEACHER" else None
