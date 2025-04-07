from django.contrib.auth import authenticate
from rest_framework import serializers
from accounts.models import User,OtpCode,Profile
from datetime import datetime,timezone,timedelta
from utils import generate_otp,send_otp
from django.utils import timezone
from utils import generate_otp,send_otp
from django.conf import settings
from django.contrib.auth.hashers import make_password







class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("شماره معتبر نیست")
        return value


    phone_number = serializers.CharField(max_length=11)
    otp = serializers.CharField(max_length=6)


    def validate(self, data):
        phone_number = data.get("phone_number")
        otp = data.get("otp")

        try:
            otp_instance = OtpCode.objects.get(phone_number=phone_number)
        except OtpCode.DoesNotExist:
            raise serializers.ValidationError("کد اشتباه است یا وجود ندارد.")

        if otp_instance.is_expired():
            otp_instance.delete()
            raise serializers.ValidationError("کد منقضی شده است. لطفاً دوباره درخواست دهید.")

        if otp_instance.otp != otp:
            otp_instance.max_otp_try -= 1
            if otp_instance.max_otp_try <= 0:
                otp_instance.delete()
                raise serializers.ValidationError("حداکثر تلاش برای وارد کردن کد تمام شده است. لطفاً دوباره درخواست دهید.")
            otp_instance.save()
            raise serializers.ValidationError(f"کد اشتباه است. تعداد تلاش باقی‌مانده: {otp_instance.max_otp_try}")

        return data


    def create(self, validated_data):
        phone_number = validated_data["phone_number"]
        otp_instance = OtpCode.objects.get(phone_number=phone_number)

        user_data = self.context['request'].session.get('user_registration')
        if not user_data:
            raise serializers.ValidationError("جلسه شما منقضی شده است. لطفاً مجدداً ثبت‌نام کنید.")

        user = User.objects.create(
            phone_number=user_data["phone_number"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            password=user_data["password"]
        )

        otp_instance.delete()
        return user


class RegisterUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    full_name = serializers.CharField(max_length=100)
    role = serializers.ChoiceField(choices=User.Types.choices)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError('شماره معتبر نیست')
        return value

    def create(self, validated_data):
        phone_number = validated_data['phone_number']

        OtpCode.objects.filter(phone_number=phone_number, otp_expiry__lt=timezone.now()).delete()

        existing_otp = OtpCode.objects.filter(phone_number=phone_number).first()
        if existing_otp and not existing_otp.is_expired():
            return {"message": "کد قبلی هنوز معتبر است."}

        code = generate_otp()
        OtpCode.objects.create(
            phone_number=phone_number,
            otp=code,
            max_otp_try=3,
            otp_expiry=timezone.now() + timedelta(minutes=5)
        )

        send_otp(phone_number, code)

        self.context['request'].session['user_registration'] = {
            "phone_number": phone_number,
            "full_name": validated_data["full_name"],
            "role": validated_data["role"],
            "password": make_password(validated_data['password'])
        }

        return {"message": "کد تأیید برای شما ارسال شد."}

class VerifyOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        phone_number = data.get("phone_number")
        otp = data.get("otp")

        try:
            otp_instance = OtpCode.objects.get(phone_number=phone_number)
        except OtpCode.DoesNotExist:
            raise serializers.ValidationError("کد اشتباه است یا وجود ندارد.")

        if otp_instance.has_expired():
            otp_instance.delete()
            raise serializers.ValidationError("کد منقضی شده است. لطفاً دوباره درخواست دهید.")

        if otp_instance.otp != otp:
            otp_instance.max_otp_try -= 1
            if otp_instance.max_otp_try <= 0:
                otp_instance.delete()
                raise serializers.ValidationError("حداکثر تلاش برای وارد کردن کد تمام شده است. لطفاً دوباره درخواست دهید.")
            otp_instance.save()
            raise serializers.ValidationError(f"کد اشتباه است. تعداد تلاش باقی‌مانده: {otp_instance.max_otp_try}")

        return data

    def create(self, validated_data):
        phone_number = validated_data["phone_number"]
        otp_instance = OtpCode.objects.get(phone_number=phone_number)
        user_data = self.context['request'].session.get('user_registration')
        if not user_data:
            raise serializers.ValidationError("جلسه شما منقضی شده است. لطفاً مجدداً ثبت‌نام کنید.")

        user = User.objects.create(
            phone_number=user_data["phone_number"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            password=user_data["password"]
        )

        otp_instance.delete()
        return user
class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)


    def validate(self, data):
        phone_number = data.get("phone_number")
        password = data.get("password")

        if phone_number and password:
            user = authenticate(phone_number=phone_number, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("حساب شما غیرفعال است")
                data["user"] = user
            else:
                raise serializers.ValidationError("شماره تلفن یا رمز عبور اشتباه است")
        else:
            raise serializers.ValidationError("لطفاً شماره تلفن و رمز عبور را وارد کنید")

        return data



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields = ["first_name", "last_name", "phone_number", "avatar"]

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and instance.user != request.user:
            raise serializers.ValidationError('شما اجازه ویرایش این پروفایل را ندارید')
        return super().update(instance, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "phone_number", "email", "role", "profile"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile',{})
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return super().update(instance, validated_data)