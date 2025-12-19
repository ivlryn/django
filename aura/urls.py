"""
URL configuration for aura project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from aura import views
from aura.views import RegisterAPI, LoginAPI , SecretExample,chart_top_categories,chart_sales_per_day,about_view
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views



urlpatterns = [
    
    path('admin/', admin.site.urls),
    
    
    path('api/menu/', views.menu_list, name='api-menu'),
    path('api/categories/', views.category, name='api-categories'),
    path('api/products/', views.product, name='api-products'),
    path('api/products/<int:id>/', views.product_detail_api, name='api-product-detail'),  # NEW: Product detail API

    path('api-blog-list', views.BlogListAPI.as_view(), name='api-blog-list'),          # NEW: List all blogs
    path('api/blogs/<slug:slug>/', views.BlogDetailAPI.as_view(), name='api-blog-detail'),  # NEW: Blog detail

    # AUTH APIs
    path("api/register/", views.RegisterAPI.as_view(), name="api-register"),
    path("api/login/", views.LoginAPI.as_view(), name="api-login"),
    path("api/secret/", views.SecretExample.as_view(), name="api-secret"),
    path("api/orders/", views.OrderListAPI.as_view(), name="api-orders"),
    
    # <-- html
    path('', views.home, name='home'),
    path('login/',
         auth_views.LoginView.as_view(
             template_name='accounts/login.html',
             redirect_authenticated_user=True   # already logged-in → home
         ),
         name='login'),

    path('logout/',
         auth_views.LogoutView.as_view(next_page='home'),
         name='logout'),
    path('signup', views.signup_page, name = 'signup'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('brand/<int:brand_id>/', views.brand_products, name='brand_products'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('profile/', views.my_account, name='profile'),
     path('api/chart/sales-per-day/',  chart_sales_per_day,  name='chart_sales_per_day'),
    path('api/chart/top-categories/', chart_top_categories, name='chart_top_categories'),
    path('about/', about_view, name='about'),
    


]
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)