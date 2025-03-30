from django.contrib.auth import authenticate
from rest_framework import serializers
from accounts.models import User,OtpCode,Profile
from datetime import datetime,timezone,timedelta
from utils import generate_otp,send_otp
from django.utils import timezone
from utils import generate_otp,send_otp
from django.conf import settings
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True,min_length=8,error_messages={'min_length':'Password must be longer than 8 character'})
    password2 = serializers.CharField(write_only=True,min_length=8,error_messages={'min_length':'Password must be longer than 8 character'})
    role = serializers.ChoiceField(choices=User.Types.choices)

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "email",
            "role",
            "password1",
            "password2"
        )
        read_only_field = ('id',)


    def validate(self,validate_data):
        if validate_data['password1'] != validate_data['password2']:
            raise serializers.ValidationError("Passsword do not match")
        return validate_data

    def validate_phone_number(self,value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError('شماره معتبر نیست')
        return value

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        OtpCode.objects.filter(phone_number=phone_number).delete()
        code = generate_otp()
        otp_code = OtpCode.objects.create(phone_number=phone_number,otp=code,max_otp_try=settings.MAX_OTP_TRY)
        send_otp(phone_number,code)
        self.context['request'].sessionp['user_registration'] = {
            "phone_number": phone_number,
            "full_name": validated_data["full_name"],
            "role": validated_data["role"],
            "password":make_password(validated_data['password1'])
        }

        return {"message": "کد تأیید برای شما ارسال شد."}



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