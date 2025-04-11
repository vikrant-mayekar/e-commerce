from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ml.app import get_top_recommendations, get_popular_products

@login_required
def recommendations_list(request):
    recommendations = get_top_recommendations(str(request.user.id), top_n=10)
    return render(request, 'recommendations/list.html', {'recommendations': recommendations})

@login_required
def personalized_recommendations(request):
    recommendations = get_top_recommendations(str(request.user.id), top_n=10)
    return render(request, 'recommendations/personalized.html', {'recommendations': recommendations})

@login_required
def popular_products(request):
    popular = get_popular_products()
    return render(request, 'recommendations/popular.html', {'popular_products': popular}) 