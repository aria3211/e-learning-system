from datetime import timedelta
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.manager import UserManager
from accounts.validators import iranian_phone_number_validator
from edue import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.timezone import now

class User(AbstractUser):
    class Types(models.TextChoices):
        STUDENT = "STUDENT", "student"
        TEACHER = "TEACHER", "teacher"

    username = None
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10,choices=Types.choices,default='student')
    profile = models.ImageField(upload_to='profiles/',null=True,blank=True)
    birth_date = models.DateField(null=True,blank=True)
    email = models.EmailField(max_length=255,unique=True)
    phone_number = models.CharField(max_length=15,unique=True)
    is_admin = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)


    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email','full_name']

    def __str__(self):
        return self.role

    def has_perms(self, perm_list, obj=None):
        return True
    @property
    def is_staff(self):
        return self.is_admin


def default_otp_expiry():
    return timezone.now() + timedelta(minutes=1)
class OtpCode(models.Model):
    phone_number = models.CharField(max_length=11, unique=True)
    otp = models.CharField(max_length=6)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.IntegerField(max_length=2, default=settings.MAX_OTP_TRY)
    otp_max_out = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.phone_number}-{self.otp}"

    def has_expired(self):
        return now() > self.otp_expiry



class Profile(models.Model):
    user = models.OneToOneField('User',on_delete=models.CASCADE,related_name='user_profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, validators=[iranian_phone_number_validator])
    avatar = models.ImageField(
        upload_to="profile/", default="profile/default.jpg")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    def get_fullname(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return "پروفایل خود را تکمیل کنید"



@receiver(post_save,sender=User)
def create_profile(sender,**kwargs):
    if kwargs['created']:
        user_instance = kwargs['instance']
        Profile.objects.create(id=user_instance.id,user=user_instance)