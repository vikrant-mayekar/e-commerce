from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommendations_list, name='recommendations_list'),
    path('personalized/', views.personalized_recommendations, name='personalized_recommendations'),
    path('popular/', views.popular_products, name='popular_products'),
] 