from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name', 'description']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class ProductDetailImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetailImage
        fields = ['productDetailImage']

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        fields = ['productDetailName', 'Description', 'skin_type', 'main_benefit', 'availability']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductDetailAPISerializer(serializers.ModelSerializer):
    details = ProductDetailSerializer(source='productdetail_set', many=True, read_only=True)
    images = ProductDetailImageSerializer(source='productdetailimage_set', many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'productName', 'price', 'productImage', 'details', 'images']

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'subtitle', 'author', 'published_date', 'read_time',
                  'category', 'thumbnail', 'featured_image', 'excerpt', 'content', 'slug']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"]
        )
        return user

# Cart & Order APIs
class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

class CheckoutSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=500)
    address_link = serializers.URLField(required=False, allow_blank=True)

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.productName', read_only=True)
    product_image = serializers.ImageField(source='product.productImage', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_name', 'product_image', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_full_name = serializers.CharField(source='shipping_address.full_name', read_only=True)
    shipping_phone = serializers.CharField(source='shipping_address.phone', read_only=True)
    shipping_address_text = serializers.CharField(source='shipping_address.address', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'total_price', 'delivery_fee',
                  'shipping_full_name', 'shipping_phone', 'shipping_address_text', 'items']