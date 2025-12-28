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

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    """Admin configuration for SellerProfile model."""
    
    list_display = ['business_name', 'get_user_email', 'rating', 'total_sales', 'is_verified_seller']
    list_filter = ['is_verified_seller', 'created_at']
    search_fields = ['business_name', 'user__email', 'tax_id']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Business Information', {
            'fields': ('business_name', 'business_description', 'business_logo')
        }),
        ('Legal Information', {
            'fields': ('tax_id', 'business_license'),
            'classes': ('collapse',)
        }),
        ('Bank Information', {
            'fields': ('bank_account_name', 'bank_account_number', 'bank_name', 'bank_routing_number'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('rating', 'total_sales', 'total_revenue')
        }),
        ('Verification', {
            'fields': ('is_verified_seller', 'verification_date')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'


@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    """Admin configuration for BuyerProfile model."""
    
    list_display = ['get_user_name', 'get_user_email', 'total_orders', 'total_spent', 'loyalty_points']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Preferences', {
            'fields': ('preferred_categories',)
        }),
        ('Metrics', {
            'fields': ('total_orders', 'total_spent', 'loyalty_points')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()
    get_user_name.short_description = 'Name'
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    