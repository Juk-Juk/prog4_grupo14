from django.db import models

class ProductEmbedding(models.Model):
    from django.conf import settings
    # Use string to avoid circular imports inn product
    product = models.OneToOneField('market.Product', on_delete=models.CASCADE, related_name="embedding",)
    model = models.CharField(max_length=100, default="gemini-embedding-001")
    vector = models.JSONField()  # Save the list of floats
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Embedding {self.product_id} ({self.model})"