from django.contrib.auth.models import BaseUserManager



class UserManager(BaseUserManager):

    def create_user(self,phone_number,email,full_name,password):
        if not phone_number:
            raise ValueError('user must have phone number')

        if not email:
            raise ValueError('user must have email')

        if not full_name:
            raise ValueError('user must have full name')
        email = self.normalize_email(email.lower()),
        user = self.model(phone_number=phone_number,email=email,full_name=full_name)

        if  password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self,phone_number,email,full_name,password):
        user = self.create_user(phone_number,email,full_name,password)
        user.is_admin = True
        user.is_teacher = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

