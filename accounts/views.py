from datetime import datetime,timezone,timedelta
import pytz as pytz
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect
from django.views import View
from .models import User,OtpCode
from accounts.forms import UserRegistraionForm,VerifyCodeForm,LoginForm,PasswordResetForm,PasswordResetConfirmForm
from utils import generate_otp,send_otp
from django.utils import timezone
from django.contrib.auth import views as auth_view
from django.contrib.auth import login, logout, authenticate


class UserRegistrationView(View):
    form_class = UserRegistraionForm
    template_name = 'accounts/user_register.html'
    def get(self,request):
        return render(request,self.template_name,{'form':self.form_class})

    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            otp = OtpCode.objects.filter(phone_number=form.cleaned_data['phone_number'])
            if otp.exists():
                otp.delete()
            code = generate_otp()
            send_otp(form.cleaned_data['phone_number'],code)
            OtpCode.objects.create(phone_number=form.cleaned_data['phone_number'],otp=code)
            request.session['user_registreation'] = {
                'phone_number':form.cleaned_data['phone_number'],
                'full_name': form.cleaned_data['full_name'],
                'role':form.cleaned_data['role'],
                'password': form.cleaned_data['password'],
            }
            messages.success(request, 'we sent you a code', 'success')
            return redirect('accounts:verify_code')
        return render(request, self.template_name, {'form': form})



class VerifyCodeView(View):
    form_class = VerifyCodeForm
    def get(self,request):
        form = self.form_class
        return render(request,"accounts/verify.html",{'form':form})
    def post(self, request):
        user_session = request.session['user_registreation']
        if not user_session:
            messages.error(request, "Session expired. Please try again.", "danger")
            return redirect("accounts:register")

        code_db = OtpCode.objects.get(phone_number=user_session['phone_number'])
        max_try = int(code_db.max_otp_try)-1

        code_db.max_otp_try = max_try
        otp_max_out = timezone.now() + timedelta(hours=1)
        code_db.otp_max_out = otp_max_out
        form = self.form_class(request.POST)
        if int(code_db.max_otp_try) == 0 and timezone.now() < code_db.otp_max_out:
            code_db.delete()
            messages.error(request, "Max OTP try reached, try after an hour", 'danger')
            return redirect('accounts:user_register')

        if form.is_valid():
            cd = form.cleaned_data


            if cd['code'] == code_db.otp:
                now = datetime.now(tz=pytz.timezone('Asia/Tehran'))
                otp_expiry = code_db.otp_expiry + timedelta(minutes=1)
                # code_db.otp_expiry = otp_expiry
                if timezone.now() > otp_expiry:
                    print("time is expired")
                    messages.error(request, "کد منقضی شده است. لطفاً کد جدیدی دریافت کنید.", "danger")
                    code_db.delete()
                    return redirect("accounts:register")
                else:
                    User.objects.create(
                        phone_number=user_session['phone_number'],
                        full_name=user_session['full_name'],
                        role=user_session['role'],
                        password=user_session['password'])
                    code_db.delete()
                    return redirect('home:home')
            else:
                # code_db.max_otp_try = int(code_db.max_otp_try)-1
                if code_db.max_otp_try == 0:
                    messages.error(request, "Max OTP try reached, try after an hour",'danger')
                    return redirect('accounts:user_register')
                code_db.save()
                messages.error(
                    request,
                    f"Incorrect OTP. {code_db.max_otp_try} attempts remaining.",
                    "danger",
                )
                return redirect('accounts:verify_code')

        return render(request, "accounts/verify.html", {"form": form})




class UserLoginView(View):
    form_class = LoginForm
    template_name = 'accounts/user_login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self,request):
        form = self.form_class()
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user = authenticate(request,phone_number=phone_number,password=password)

            if user is not None:
                login(request,user)
                messages.success(request,'با موفقیت وارد شدید','success')
                if user.role == 'TEACHER':
                    return redirect('dashboard:teacher_panel')
                return redirect('dashboard:student_panel')
        else:
            messages.error(request, "نام کاربری یا رمز عبور اشتباه است!", "danger")

        return render(request, self.template_name, {"form": form})


class UserLogoutView(View):

    def get(self, request):
        logout(request)
        messages.success(request, "با موفقیت خارج شدید.", "success")
        return redirect("accounts:login")