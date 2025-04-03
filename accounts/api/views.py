from urllib.parse import urljoin

from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.urls import reverse
from rest_framework import status,generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from edue import settings
from .serializers import RegisterUserSerializer,UserLoginSerializer,ProfileSerializer,UserProfileSerializer,VerifyOtpSerializer
from accounts.models import User


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
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            return Response({"message": "کاربر با موفقیت ایجاد شد.", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
