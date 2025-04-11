from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from products.models import PurchaseHistory, Wishlist, Product
from ml.app import get_top_recommendations

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'users/login.html')

@login_required
def dashboard(request):
    orders = PurchaseHistory.objects.filter(user=request.user).order_by('-purchase_date')[:5]
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    # Get recommendations for the current user
    recommendations = get_top_recommendations(str(request.user.id), top_n=5)
    
    # Get product details for recommendations
    recommended_products = []
    for rec in recommendations:
        try:
            # Use the product name to look up the product instead of ID
            product = Product.objects.get(name=rec['Product_ID'])
            recommended_products.append({
                'product': product,
                'similarity_score': rec['Similarity_Score'],
                'final_score': rec['Final_Score']
            })
        except Product.DoesNotExist:
            continue
    
    context = {
        'orders': orders,
        'wishlist_items': wishlist_items,
        'recommended_products': recommended_products,
    }
    return render(request, 'users/dashboard.html', context) 