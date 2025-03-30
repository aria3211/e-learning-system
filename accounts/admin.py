from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OtpCode, Profile
from .forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import Group




class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email','phone_number','role','full_name')
    list_filter = ('phone_number','email','is_teacher')
    fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'full_name', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_teacher','role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'full_name','role', 'password1', 'password2'),
        }),
    )
    # add_fieldsets = (
    #     (None,{'fields':('email','phone_number','full_name', 'password1', 'password2')})
    # )
    search_fields = ('email', 'phone_number')
    ordering = ('phone_number',)
    filter_horizontal = ()


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "phone_number")
    searching_fields = ("user", "first_name", "last_name", "phone_number")


admin.site.unregister(Group)
admin.site.register(User,UserAdmin)
admin.site.register(OtpCode)
