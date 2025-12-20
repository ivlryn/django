from django.http import JsonResponse
from .models import *
from .serializers import *
from django.shortcuts import render,  get_object_or_404, redirect
from django.conf.urls.static import static
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .cart import Cart
from django.contrib import messages
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from .serializers import (
    MenuSerializer, CategorySerializer, ProductDetailAPISerializer,
    BlogPostSerializer, OrderSerializer
)
from .serializers import ProductDetailAPISerializer  # Use the detailed serializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from rest_framework.authentication import TokenAuthentication
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json
from django.http import JsonResponse
from django.core.paginator import Paginator






def menu_list (request) :
    menus = Menu.objects.all()
    serializers = MenuSerializer(menus, many = True)
    return JsonResponse({"menus": serializers.data},safe=False)

def category (request) :
    categories = Category.objects.all()
    serializers = CategorySerializer(categories, many = True)
    return JsonResponse({"categories": serializers.data},safe=False)


def product (request) :
    products = Product.objects.all()
    serializers = ProductSerializer(products, many = True)
    return JsonResponse({"products": serializers.data},safe=False)



def home(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products_qs = Product.objects.all()  # Use a separate variable for the full queryset

    # Pagination
    paginator = Paginator(products_qs, 12)  # 12 products per page (change if needed, e.g., 9, 15, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)  # This handles invalid pages gracefully

    # Latest 3 published blog posts (unchanged)
    blog_posts = BlogPost.objects.filter(is_published=True).select_related()[:3]

    context = {
        'categories': categories,
        'brands': brands,
        'products': products,       # Now a Page object (paginated)
        'blog_posts': blog_posts,   
    }
    return render(request, "home.html", context)

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    details = ProductDetail.objects.filter(productID=product).first()
    images = ProductDetailImage.objects.filter(productID=product)

    return render(request, 'product_detail.html', {
        'product': product,
        'details': details,
        'images': images,
    })
    
    
def brand_products(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    # FIX: Query Product, not ProductDetail
    products = Product.objects.filter(productdetail__brandID=brand).distinct()
    
    return render(request, 'productbrand.html', {
        'brand': brand,
        'products': products
    })


class RegisterAPI(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "User registered successfully",
                "token": token.key,
                "user": UserSerializer(user).data
            })
        return Response(serializer.errors, status=400)



class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful",
            "token": token.key,
            "user": UserSerializer(user).data
        })
        
def signup_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'accounts/signup.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'accounts/signup.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created – please log in')
        return redirect('login')
    return render(request, 'accounts/signup.html')


# API LOGIN → returns TOKEN
@api_view(["POST"])
def api_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if not user:
        return JsonResponse({"error": "Invalid credentials"}, status=400)

    token, created = Token.objects.get_or_create(user=user)
    return JsonResponse({"token": token.key})

class SecretExample(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes    = [IsAuthenticated]

    def get(self, request):
        return Response({"secret": f"hello {request.user.username}"})
    
#cart
# --------------------  cart  --------------------
def cart_view(request):
    return render(request, 'cart.html')

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))  # ← THIS LINE WAS MISSING!
        cart.add(product=product, quantity=quantity)    # ← Now respects your selector
        messages.success(request, f"Added {quantity} × {product.productName} to cart")
    else:
        cart.add(product=product, quantity=1)

    # Stay on same page (product detail) — better UX
    return redirect(request.META.get('HTTP_REFERER', 'home'))  # stay on same page

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart')


# --------------------  checkout  --------------------
@login_required
def checkout_view(request):
    cart = Cart(request)

    # If cart is empty → send back to cart
    if not cart:
        messages.info(request, "Your cart is empty")
        return redirect('cart')

    if request.method == 'POST':
        # Save address
        address = ShippingAddress.objects.create(
            user=request.user,
            full_name=request.POST['full_name'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            address_link=request.POST.get('address_link', '')
        )

        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=address,
            total_price=cart.get_total_price() + Decimal('2.00'),
            delivery_fee=Decimal('2.00')
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )

        cart.clear()
        messages.success(request, "Order placed successfully!")
        return redirect('checkout_success')

    # ← THIS WAS MISSING THIS LINE
    context = {
        'cart': cart
    }
    return render(request, 'checkout.html', context)   # <-- your new template


def checkout_success(request):
    return render(request, 'ordersuc.html')

def cart_update(request):
    """AJAX: change quantity for one product."""
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    quantity   = int(request.POST.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id)
    cart.add(product, quantity)          # our add() replaces the quantity
    cart.save()

    item_total = cart.cart[str(product_id)]['quantity'] * Decimal(cart.cart[str(product_id)]['price'])
    grand      = cart.get_grand_total()

    return JsonResponse({
        'item_total': float(item_total),
        'grand_total': float(grand),
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'my_orders.html', {'orders': orders})
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'my_orders.html', {'orders': orders})

@login_required
def my_account(request):
    orders = Order.objects.filter(user=request.user)\
             .prefetch_related('items__product')\
             .order_by('-created_at')

    return render(request, 'accounts/profile.html', {
        'orders': orders
    })


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    qty = int(request.POST.get("quantity", 1))
    product = get_object_or_404(Product, id=product_id)

    if qty < 1:
        qty = 1

    cart.cart[str(product_id)]["quantity"] = qty
    cart.save()

    return JsonResponse({
        "success": True,
        "item_total": float(cart.cart[str(product_id)]["quantity"]) * float(cart.cart[str(product_id)]["price"]),
        "subtotal": float(cart.get_total_price()),
        "grand_total": float(cart.get_grand_total()),
    })
    
def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Optional: Get 3 related posts (same category)
    related_posts = BlogPost.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id)[:3]

    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog_detail.html', context)


def product_detail_api(request, id):
    product = get_object_or_404(Product, id=id)
    serializer = ProductDetailAPISerializer(product)
    return JsonResponse(serializer.data)


class BlogListAPI(APIView):
    def get(self, request):
        blogs = BlogPost.objects.filter(is_published=True).order_by('-published_date')
        serializer = BlogPostSerializer(blogs, many=True)
        return Response(serializer.data)

# Blog Detail API
class BlogDetailAPI(APIView):
    def get(self, request, slug):
        blog = get_object_or_404(BlogPost, slug=slug, is_published=True)
        serializer = BlogPostSerializer(blog)
        return Response(serializer.data)
    
    
# AUTH: List User's Orders
class OrderListAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Requires login + token

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    

# ---------- 1.  Sales per day (last 30 days) ----------
def chart_sales_per_day(request):
    """
    Returns JSON like
    {labels:['19 Nov','20 Nov',...], data:[120.50, 95.00, ...]}
    """
    days  = int(request.GET.get('days', 30))
    end   = timezone.now().date()
    start = end - timedelta(days=days-1)

    qs = (Order.objects
          .filter(created_at__date__gte=start,
                  created_at__date__lte=end)
          .values('created_at__date')
          .annotate(total=Sum('total_price'))
          .order_by('created_at__date'))

    # build zero-filled list
    labels, data = [], []
    for i in range(days):
        d = start + timedelta(days=i)
        day_str = d.strftime('%d %b')
        labels.append(day_str)
        row = [x for x in qs if x['created_at__date'] == d]
        data.append(float(row[0]['total']) if row else 0.0)

    return JsonResponse({'labels': labels, 'data': data})


# ---------- 2.  Top categories (qty sold) ----------
def chart_top_categories(request):
    """
    Returns JSON like
    {labels:['Lipstick','Foundation',...], data:[45,33,...]}
    """
    top = (OrderItem.objects
           .values('product__categoryID__categoryName')
           .annotate(qty=Sum('quantity'))
           .order_by('-qty')[:6])
    labels = [x['product__categoryID__categoryName'] for x in top]
    data   = [x['qty'] for x in top]
    return JsonResponse({'labels': labels, 'data': data})

def about_view(request):
    return render(request, 'about.html')