from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from products import views as product_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('products/', include('products.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('ml/', include('ml.urls')),
    path('', user_views.user_login, name='login'),  # Root URL
    path('login/', user_views.user_login, name='login'),  # /login/ URL
    path('register/', user_views.register, name='register'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('products/<int:product_id>/', product_views.product_detail, name='product_detail'),
    path('wishlist/', product_views.wishlist, name='wishlist'),
    path('purchase-history/', product_views.purchase_history, name='purchase_history'),
    path('add-to-wishlist/<int:product_id>/', product_views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', product_views.remove_from_wishlist, name='remove_from_wishlist'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 