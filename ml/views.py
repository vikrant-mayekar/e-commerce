from django.http import JsonResponse
from django.conf import settings
from .app import (
    get_top_recommendations,
    get_query_recommendations,
    update_user_preferences,
    update_product_popularity,
    get_preferences as ml_get_preferences
)

def recommend(request, customer_id):
    try:
        results = get_top_recommendations(customer_id)
        # Record view interaction for each recommended product
        for product in results:
            update_product_popularity(product['Product_ID'], 'view')
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def search(request, customer_id):
    query = request.GET.get("query", "")
    results = get_query_recommendations(customer_id, query)
    # Record view interaction for search results
    for product in results:
        update_product_popularity(product['Product_ID'], 'view')
    return JsonResponse(results, safe=False)

def click(request, customer_id, product_id):
    try:
        # Get product data
        from products.models import Product
        product = Product.objects.get(id=product_id)
        product_data = {
            'Product_ID': str(product.id),
            'Brand': product.brand,
            'Category': product.category,
            'Subcategory': product.subcategory
        }
        
        # Update user preferences based on clicked product
        update_user_preferences(customer_id, product_data)
        
        # Record click interaction
        update_product_popularity(product_id, 'click')
        
        return JsonResponse({
            "status": "success",
            "message": f"Click recorded for {customer_id} on product {product_id}"
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_preferences(request, customer_id):
    try:
        preferences = ml_get_preferences(customer_id)
        return JsonResponse(preferences, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)  # Return empty list on error 