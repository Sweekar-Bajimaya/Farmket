from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, BuyerProfile, SellerProfile
from django.utils.html import format_html

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_active', 'user_type')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('User',{
            'fields': ('user_type', 'email', 'first_name', 'last_name', 'password')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_type', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'updated_at']
    
    def get_user_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_user_name.short_description = 'Full Name'
    
    def get_user_email(self, obj):
        return obj.email
    get_user_email.short_description = 'Email Address'

