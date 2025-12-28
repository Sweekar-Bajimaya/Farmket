from django.contrib import admin
from .models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1   
    fields = ('image', 'alt_text')
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller__seller_profile__business_name', 'final_price', 'stock_quantity', 'status', 'is_featured', 'created_at')
    list_filter = ('category', 'status', 'is_featured', 'created_at')
    search_fields = ('name', 'slug', 'sku', 'seller__email', 'seller__seller_profile__business_name')
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Seller',{
            'fields': ('seller',)
        }),
        ('Product Info', {
            'fields': ('name', 'slug', 'sku', 'category')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'unit')
        }),
        ('Status', {
            'fields': ('status', 'is_featured')
        })
    )
    
    def final_price(self, obj):
        return f"${obj.final_price}" 
    final_price.short_description = 'Price'
    final_price.admin_order_field = 'price'
    
    
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'alt_text')
    ordering = ('-created_at',)      
