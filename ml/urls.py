from django.urls import path
from . import views

urlpatterns = [
    path('recommend/<str:customer_id>/', views.recommend, name='recommend'),
    path('search/<str:customer_id>/', views.search, name='search'),
    path('click/<str:customer_id>/<str:product_id>/', views.click, name='click'),
    path('preferences/<str:customer_id>/', views.get_preferences, name='preferences'),
] 