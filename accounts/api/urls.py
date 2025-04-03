from django.urls import path,include

from rest_framework import routers

from accounts.api.views import StudentProfileView, TeacherProfileView, RegisterUserAPIView,VerifyOTPAPIView

app_name = 'accounts'


router = routers.DefaultRouter()
router.register(r'Student_users', StudentProfileView, basename='susers')
router.register(r'Teacher_users', TeacherProfileView, basename='tusers')
urlpatterns = [

    # path('api/auth/', include('dj_rest_auth.urls')),  # لاگین، لاگ‌اوت، تغییر رمز عبور
    # path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  # ثبت‌نام
    path('api/auth/google/', include('allauth.socialaccount.urls')),  # احراز هویت گوگل
    # path('api/auth/', include('dj_rest_auth.urls')),
    path('profile/student/', StudentProfileView.as_view(), name='student-profile'),
    path('profile/teacher/', TeacherProfileView.as_view(), name='teacher-profile'),
    path("register/", RegisterUserAPIView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify_otp"),
    # path('',include(router.urls))

]