from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Wishlist, PurchaseHistory, ProductView
from recommendations.recommender import Recommender

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/list.html', {'products': products})

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Track product view
    ProductView.objects.create(user=request.user, product=product)
    
    # Get recommendations
    recommender = Recommender()
    recommendations = recommender.generate_recommendations(request.user.id)
    
    # Check if product is in wishlist
    in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    return render(request, 'products/detail.html', {
        'product': product,
        'recommendations': recommendations,
        'in_wishlist': in_wishlist
    })

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def purchase_history(request):
    purchases = PurchaseHistory.objects.filter(user=request.user)
    return render(request, 'products/purchase_history.html', {'purchases': purchases})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('product_detail', product_id=product_id)

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('wishlist') 