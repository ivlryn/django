from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse

class Menu (models.Model) : 
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=900)
    
    def __str__(self):
        return self.name 

# start from here

class Category(models.Model):
    categoryName = models.CharField(max_length=200)
    description = models.CharField(max_length=900,null=True)
    def __str__(self):         
        return self.categoryName 

class Brand(models.Model):
    brandName = models.CharField(max_length=200)
    brandDescription = models.CharField(max_length=900,null=True)
    def __str__(self):         
        return self.brandName 
    

class Product(models.Model):
    productName = models.CharField(max_length=200)
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    price = models.CharField(max_length=200)
    productImage = models.ImageField(upload_to='images/Products/',null=True,blank=True)
    productDate = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):         
        return self.productName

class ProductDetail(models.Model):
    productDetailName = models.CharField(max_length=200, null=True)
    productID = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    brandID = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    Description =  models.CharField(max_length=1000, null=True)
    skin_type = models.CharField(max_length=1000, null=True)
    main_benefit = models.CharField(max_length=1000, null=True)
    availability = models.CharField(max_length=200, null=True)
    productDetailDate = models.DateTimeField (auto_now_add=True, null=True)
    def __str__(self):         
        return f'{self.productID.productName} - {self.productDetailName}'
    
class ProductDetailImage(models.Model):
    productDetailImageName = models.CharField(max_length=200, null=True)
    productID = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    productDetailImage = models.ImageField(upload_to='images/productDetail/',null=True,blank=True)
    imageDate = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):         
        return f'{self.productID.productName} - {self.productDetailImageName}'


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField("Full Name", max_length=200)
    phone = models.CharField("Phone / Telegram", max_length=50)
    address = models.CharField("Delivery Address", max_length=500)
    address_link = models.URLField("Address Link (Optional)", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.phone}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=2.00)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        if self.product:
            return f"{self.product.productName} (x{self.quantity}) - Order {self.order.id}"
        else:
            return f"Deleted Product (x{self.quantity}) - Order {self.order.id}"
    
    
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    author = models.CharField(max_length=100, default="Luxé Beauty Team")
    published_date = models.DateField(auto_now_add=True)
    read_time = models.PositiveIntegerField(help_text="Read time in minutes", default=5)

    CATEGORY_CHOICES = [
        ('routine', 'Skincare Routine'),
        ('ingredients', 'Ingredients'),
        ('seasonal', 'Seasonal Tips'),
        ('tips', 'Beauty Tips'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='tips')

    # Images
    thumbnail = models.ImageField(upload_to='images/blog/thumbnails/', help_text="Thumbnail for grid (recommended: 400x300 or 1:1)")
    featured_image = models.ImageField(upload_to='images/blog/featured/', blank=True, null=True, help_text="Large image for article page")

    # Content
    excerpt = models.TextField(max_length=500, help_text="Short teaser shown on homepage")
    content = models.TextField(help_text="Full article content – you can use <p>, <h2>, <ul>, etc.")

    # URL & Visibility
    slug = models.SlugField(unique=True, max_length=200, help_text="e.g. double-cleansing-guide")
    is_published = models.BooleanField(default=True, help_text="Uncheck to hide from site")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', args=[self.slug])

    class Meta:
        ordering = ['-published_date']