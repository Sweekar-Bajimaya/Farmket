from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import SellerProfile, User
from common.constants import (
    MAX_PRICE_DIGITS,
    PRODUCT_STATUS_CHOICES,
    RATING_DECIMAL_PLACES,
    RATING_MAX_DIGITS,
    STATUS_AVAILABLE,
    STATUS_OUT_OF_STOCK,
    STATUS_DISCONTINUED,
    UNIT_KG,
    UNIT_TYPE_CHOICES,
    MAX_PRODUCT_NAME_LENGTH,
    MAX_SLUG_LENGTH,
    MAX_SKU_LENGTH,
    MAX_CATEGORY_NAME_LENGTH,
    MAX_DECIMAL_PLACES,
    MAX_UNIT_LENGTH,
)

class Category(models.Model):
    """
    Product Category for organizing fruits and vegetables.
    """
    name = models.CharField(max_length=MAX_CATEGORY_NAME_LENGTH, unique=True)
    slug = models.SlugField(max_length=MAX_SLUG_LENGTH, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        

class Product(models.Model):
    """
    Product model representing fruits and vegetables.
    """
    seller = models.ForeignKey(
        SellerProfile,
        on_delete=models.CASCADE,
        related_name='products',
    )
    
    name = models.CharField(max_length=MAX_PRODUCT_NAME_LENGTH, db_index=True)
    slug = models.SlugField(max_length=MAX_SLUG_LENGTH, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=False,
        related_name='products'
    )
    price = models.DecimalField(max_digits=MAX_PRICE_DIGITS, decimal_places=MAX_DECIMAL_PLACES, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    
    stock_quantity = models.PositiveIntegerField(default=0, db_index=True)
    unit = models.CharField(max_length=MAX_UNIT_LENGTH, choices=UNIT_TYPE_CHOICES, default=UNIT_KG)
    sku = models.CharField(max_length=MAX_SKU_LENGTH, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES, default=STATUS_AVAILABLE, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    
    average_rating = models.DecimalField(
        max_digits=RATING_MAX_DIGITS,
        decimal_places=RATING_DECIMAL_PLACES,
        default=0.00,
        db_index=True
    )
    total_reviews = models.PositiveIntegerField(default=0)
    total_sold = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['seller']),
            models.Index(fields=['total_sold']),
            models.Index(fields=['average_rating']),
        ]   
    
    def __str__(self):
        return f"{self.name} - {self.seller.business_name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            slug_conflict_qs = Product.objects.filter(slug=slug)
            if self.pk:
                slug_conflict_qs = slug_conflict_qs.exclude(pk=self.pk)
            while slug_conflict_qs.exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                slug_conflict_qs = Product.objects.filter(slug=slug)
                if self.pk:
                    slug_conflict_qs = slug_conflict_qs.exclude(pk=self.pk)
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.discount_price and self.price > 0:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount, 2)
        return 0.00
    
    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
    

class ProductImage(models.Model):
    """
    Image for every product.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        indexes = [
            models.Index(fields=['product']),
        ]
        
    def __str__(self):
        return f"Image for {self.product.name}"  
        