from django.contrib import admin
from .models import Menu, Category, Product, ProductDetail, ProductDetailImage, Brand,Order, OrderItem
from .models import *
from django.shortcuts import render
from django.db.models import Sum, Count
from django.urls import path
from django.utils import timezone   
from datetime import datetime
from django.utils.html import format_html



# --- 1. Define the Inline Class ---
# This class tells Django how to display ProductDetailImage forms 
# *inside* the Product admin page.
class ProductDetailImageInline(admin.TabularInline):
    # The model this inline is managing
    model = ProductDetailImage
    
    # The fields to display in the inline form
    fields = ['productDetailImageName', 'productDetailImage']
    
    # Specifies how many extra (blank) forms to show initially.
    # Setting this to 3 means you'll see 3 blank forms ready for upload
    extra = 3 
    
    # Optional: You can set min_num or max_num if you want to enforce limits
    # min_num = 1 # Ensures at least one image is uploaded
    # max_num = 10 # Limits the total number of images
    



class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductDetailImageInline]
    
    # Your desired order: ID → Product Name → Category → Price → Image
    list_display = ('id', 'productName', 'categoryID', 'price', 'product_thumbnail')
    
    list_per_page = 20
    search_fields = ('productName', 'id')
    list_filter = ('categoryID',)

    def product_thumbnail(self, obj):
        if obj.productImage:
            return format_html(
                '<img src="{}" width="70" height="70" style="object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.productImage.url
            )
        return "(No image)"
    product_thumbnail.short_description = "Image"

class OrderItemAdmin(admin.ModelAdmin):
    # This defines the columns in the list view
    list_display = ('id', 'order', 'product_thumbnail', 'product_name', 'quantity', 'price', 'total_item_price')
    
    # Filter and search capabilities
    list_filter = ('order__created_at',)
    search_fields = ('product__productName', 'order__id')
    
    # Optional: make some fields read-only to prevent accidental data changes
    readonly_fields = ('product_thumbnail',)

    # 1. Helper to show the product name from the relationship
    def product_name(self, obj):
        return obj.product.productName
    product_name.short_description = 'Product'

    # 2. Helper to show the image of the product associated with this item
    def product_thumbnail(self, obj):
        if obj.product and obj.product.productImage:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.product.productImage.url
            )
        return "(No image)"
    product_thumbnail.short_description = "Image"

    # 3. Helper to calculate total for that specific line (Price x Qty)
    def total_item_price(self, obj):
        return obj.price * obj.quantity
    total_item_price.short_description = "Total Price"
    # This defines the columns in the list view
    list_display = ('id', 'order', 'product_thumbnail', 'product_name', 'quantity', 'price', 'total_item_price')
    
    # Filter and search capabilities
    list_filter = ('order__created_at',)
    search_fields = ('product__productName', 'order__id')
    
    # Optional: make some fields read-only to prevent accidental data changes
    readonly_fields = ('product_thumbnail',)

    # 1. Helper to show the product name from the relationship
    def product_name(self, obj):
        return obj.product.productName
    product_name.short_description = 'Product'

    # 2. Helper to show the image of the product associated with this item
    def product_thumbnail(self, obj):
        if obj.product and obj.product.productImage:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.product.productImage.url
            )
        return "(No image)"
    product_thumbnail.short_description = "Image"

    # 3. Helper to calculate total for that specific line (Price x Qty)
    def total_item_price(self, obj):
        return obj.price * obj.quantity
    total_item_price.short_description = "Total Price"    

    
class MyAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        # Get date range from GET parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Parse dates (default to all time if not provided)
        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                # Include the full end day
                end_date = timezone.datetime.combine(end_date, timezone.datetime.max.time())
            except ValueError:
                pass

        # Base queryset
        orders_qs = Order.objects.all()
        if start_date:
            orders_qs = orders_qs.filter(created_at__gte=start_date)
        if end_date:
            orders_qs = orders_qs.filter(created_at__lte=end_date)

        # Calculations
        total_sales = orders_qs.aggregate(total=Sum('total_price'))['total'] or 0
        total_orders = orders_qs.count()

        recent_orders = orders_qs.select_related('user').order_by('-created_at')[:10]

        top_products = OrderItem.objects.filter(order__in=orders_qs).values(
            'product__productName'
        ).annotate(
            total_qty=Sum('quantity')
        ).order_by('-total_qty')[:5]

        extra_context = extra_context or {}
        extra_context.update({
            'total_sales': total_sales,
            'total_orders': total_orders,
            'recent_orders': recent_orders,
            'top_products': top_products,
            'start_date': start_date_str or '',
            'end_date': end_date_str or '',
        })
        return super().index(request, extra_context=extra_context)

# Keep this line
admin.site = MyAdminSite()



# Register all other models directly as before
admin.site.register(Category)
admin.site.register(ProductDetail)
admin.site.register(Brand)
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Product, ProductAdmin)
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published_date', 'read_time', 'is_published']
    list_filter = ['category', 'is_published', 'published_date']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ['published_date']

