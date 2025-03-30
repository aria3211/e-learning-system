from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField,AuthenticationForm as authen_form
from .models import User
from django.core.exceptions import ValidationError



class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='password',widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password',widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number','email','full_name')

    def clean_password2(self):
        cd = self.cleaned_data
        password1 = cd.get('password1')
        password2 = cd.get('password2')
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError('Passwords dont match!!')
        return password2
    def save(self,commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text="you can change password using <a href=\"../password/\> this form")
    class Meta:
        model = User
        fields = ["email", "phone_number", "full_name", "is_teacher", "is_admin","last_login"]

    def clean_password(self):
        # پسورد رو همون مقدار ذخیره شده برمی‌گردونه
        return self.initial["password"]



class UserRegistraionForm(forms.Form):
    phone_number = forms.CharField(max_length=11)
    full_name = forms.CharField(label='Full Name')
    email = forms.EmailField()
    role = forms.ChoiceField(label="Select Your Role",choices={'teacher':'Teacher','student':'Student'},widget=forms.RadioSelect)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        cd = self.cleaned_data
        email = User.objects.filter(email=cd['email'])
        if email:
            raise ValidationError('email is already exisits')


class VerifyCodeForm(forms.Form):
    code = forms.CharField()


class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=11)
    password = forms.CharField(widget=forms.PasswordInput,label='password')


class PasswordResetForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label="شماره موبایل")


class PasswordResetConfirmForm(forms.Form):
    otp = forms.CharField(max_length=6, label="کد تأیید")
    new_password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور جدید")

