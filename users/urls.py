from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),  # Root URL
    path('login/', views.user_login, name='login'),  # /login/ URL
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
] 