from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
from .constants import (
    USER_TYPE_CHOICES,
    USER_TYPE_BUYER,
    USER_TYPE_SELLER,
    PHONE_REGEX,
    PHONE_ERROR_MESSAGE,
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_ADDRESS_LENGTH,
    MAX_CITY_LENGTH,
    MAX_STATE_LENGTH,
    MAX_POSTAL_CODE_LENGTH,
    MAX_COUNTRY_LENGTH,
    MAX_BUSINESS_NAME_LENGTH,
    MAX_TAX_ID_LENGTH,
    MAX_BUSINESS_LICENSE_LENGTH,
    MAX_BANK_ACCOUNT_LENGTH,
    MAX_BANK_NAME_LENGTH,
    MAX_BANK_ROUTING_LENGTH,
    RATING_MAX_DIGITS,
    RATING_DECIMAL_PLACES,
    REVENUE_MAX_DIGITS,
    REVENUE_DECIMAL_PLACES,
)


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for Farmket e-commerce platform.
    Supports two user types: BUYER and SELLER.
    Uses email for authentication instead of username.
    """
    
    # Basic Information
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        db_index=True,
        verbose_name='Email Address'
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        db_index=True,
        verbose_name='User Type'
    )
    
    # Personal Information
    first_name = models.CharField(max_length=MAX_NAME_LENGTH)
    last_name = models.CharField(max_length=MAX_NAME_LENGTH)
    
    phone_regex = RegexValidator(
        regex=PHONE_REGEX,
        message=PHONE_ERROR_MESSAGE
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=MAX_PHONE_LENGTH,
        blank=True,
        null=True
    )
    
    # Profile
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    # Address Information
    address = models.CharField(max_length=MAX_ADDRESS_LENGTH, blank=True)
    city = models.CharField(max_length=MAX_CITY_LENGTH, blank=True, db_index=True)
    state = models.CharField(max_length=MAX_STATE_LENGTH, blank=True)
    
    # Account Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email', 'user_type']),
            models.Index(fields=['user_type', 'is_active']),
            models.Index(fields=['city', 'user_type']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
    
    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the user's first name."""
        return self.first_name
    
    @property
    def is_buyer(self):
        """Check if user is a buyer."""
        return self.user_type == USER_TYPE_BUYER
    
    @property
    def is_seller(self):
        """Check if user is a seller."""
        return self.user_type == USER_TYPE_SELLER


class SellerProfile(models.Model):
    """
    Extended profile for sellers with business-specific information.
    Separate model to keep User model lean and optimize queries.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='seller_profile'
    )
    
    # Business Information
    business_name = models.CharField(
        max_length=MAX_BUSINESS_NAME_LENGTH,
        unique=True,
        db_index=True
    )
    business_description = models.TextField(blank=True)
    business_logo = models.ImageField(
        upload_to='business_logos/',
        blank=True,
        null=True
    )
    
    # Tax and Legal
    tax_id = models.CharField(max_length=MAX_TAX_ID_LENGTH, blank=True)
    business_license = models.CharField(max_length=MAX_BUSINESS_LICENSE_LENGTH, blank=True)
    
    # Bank Information for payments
    bank_account_name = models.CharField(max_length=MAX_BUSINESS_NAME_LENGTH, blank=True)
    bank_account_number = models.CharField(max_length=MAX_BANK_ACCOUNT_LENGTH, blank=True)
    bank_name = models.CharField(max_length=MAX_BANK_NAME_LENGTH, blank=True)
    bank_routing_number = models.CharField(max_length=MAX_BANK_ROUTING_LENGTH, blank=True)
    
    # Seller Metrics
    rating = models.DecimalField(
        max_digits=RATING_MAX_DIGITS,
        decimal_places=RATING_DECIMAL_PLACES,
        default=0.00,
        db_index=True
    )
    total_sales = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(
        max_digits=REVENUE_MAX_DIGITS,
        decimal_places=REVENUE_DECIMAL_PLACES,
        default=0.00
    )
    
    # Status
    is_verified_seller = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'seller_profiles'
        verbose_name = 'Seller Profile'
        verbose_name_plural = 'Seller Profiles'
        indexes = [
            models.Index(fields=['rating', 'is_verified_seller']),
            models.Index(fields=['business_name']),
        ]
    
    def __str__(self):
        return f"{self.business_name} - {self.user.email}"


class BuyerProfile(models.Model):
    """
    Extended profile for buyers with shopping preferences.
    Separate model to optimize queries and keep data organized.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='buyer_profile'
    )
    
    # Preferences
    preferred_categories = models.JSONField(default=list, blank=True)
    
    # Buyer Metrics
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(
        max_digits=REVENUE_MAX_DIGITS,
        decimal_places=REVENUE_DECIMAL_PLACES,
        default=0.00
    )
    
    # Loyalty
    loyalty_points = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'buyer_profiles'
        verbose_name = 'Buyer Profile'
        verbose_name_plural = 'Buyer Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Buyer"