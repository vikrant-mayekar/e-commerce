import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from django.contrib.auth import get_user_model
from products.models import Product, PurchaseHistory, ProductView
from .models import UserPreferences, Recommendation

User = get_user_model()

class Recommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def get_user_product_matrix(self):
        """Create user-product interaction matrix"""
        users = User.objects.all()
        products = Product.objects.all()
        matrix = np.zeros((len(users), len(products)))
        
        # Fill matrix with purchase history
        for purchase in PurchaseHistory.objects.all():
            user_idx = list(users).index(purchase.user)
            product_idx = list(products).index(purchase.product)
            matrix[user_idx, product_idx] = 1
            
        # Add view history with lower weight
        for view in ProductView.objects.all():
            user_idx = list(users).index(view.user)
            product_idx = list(products).index(view.product)
            matrix[user_idx, product_idx] += 0.5
            
        return matrix, users, products

    def collaborative_filtering(self, user_id, n_recommendations=5):
        """Generate recommendations using collaborative filtering"""
        matrix, users, products = self.get_user_product_matrix()
        user_idx = list(users).index(User.objects.get(id=user_id))
        
        # Calculate user similarity
        user_similarity = cosine_similarity(matrix)
        
        # Get similar users
        similar_users = np.argsort(user_similarity[user_idx])[::-1][1:6]
        
        # Get products liked by similar users
        recommendations = []
        for similar_user in similar_users:
            liked_products = np.where(matrix[similar_user] > 0)[0]
            for product_idx in liked_products:
                if matrix[user_idx, product_idx] == 0:  # Not already interacted with
                    product = products[product_idx]
                    score = user_similarity[user_idx, similar_user]
                    recommendations.append((product, score))
        
        # Sort by score and return top n
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]

    def content_based_filtering(self, user_id, n_recommendations=5):
        """Generate recommendations using content-based filtering"""
        user = User.objects.get(id=user_id)
        
        # Check if user preferences exist
        try:
            preferences = UserPreferences.objects.get(user=user)
        except UserPreferences.DoesNotExist:
            # If no preferences, return empty list
            return []
        
        # Get product descriptions
        products = Product.objects.all()
        descriptions = [f"{p.name} {p.description} {p.category}" for p in products]
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(descriptions)
        
        # Calculate similarity between products
        product_similarity = cosine_similarity(tfidf_matrix)
        
        # Get user's previously viewed products
        viewed_products = ProductView.objects.filter(user=user).values_list('product_id', flat=True)
        
        recommendations = []
        for viewed_id in viewed_products:
            product_idx = list(products).index(Product.objects.get(id=viewed_id))
            similar_products = np.argsort(product_similarity[product_idx])[::-1][1:6]
            
            for similar_idx in similar_products:
                product = products[similar_idx]
                if product.id not in viewed_products:
                    score = product_similarity[product_idx, similar_idx]
                    recommendations.append((product, score))
        
        # Sort by score and return top n
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]

    def generate_recommendations(self, user_id, n_recommendations=5):
        """Generate hybrid recommendations"""
        collab_recs = self.collaborative_filtering(user_id, n_recommendations)
        
        # Try to get content-based recommendations
        try:
            content_recs = self.content_based_filtering(user_id, n_recommendations)
        except Exception:
            # If there's any error with content-based filtering, just use collaborative
            content_recs = []
        
        # If we have no recommendations at all, return empty list
        if not collab_recs and not content_recs:
            return []
        
        # Combine and deduplicate recommendations
        all_recs = {}
        for product, score in collab_recs + content_recs:
            if product.id not in all_recs or score > all_recs[product.id][1]:
                all_recs[product.id] = (product, score)
        
        # Sort by score and return top n
        recommendations = sorted(all_recs.values(), key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations] 