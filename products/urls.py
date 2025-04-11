from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('purchase-history/', views.purchase_history, name='purchase_history'),
] 