from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_categories = models.JSONField(default=list)
    price_range = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    recommendation_type = models.CharField(max_length=50)  # e.g., 'collaborative', 'content-based'

    class Meta:
        ordering = ['-score'] 