# Create your models here.
from django.db import models
from django.contrib.postgres.indexes import Index
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField
from pgvector.django import HnswIndex


# Magazine model
class MagazineInformation(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_date = models.DateField()
    category = models.TextField()  # Store multiple categories as a single text field
    content = models.TextField()
    publication_country = models.CharField(max_length=100)
    revenue_generated = models.CharField(max_length=255)

    search_vector = SearchVectorField(null=True)  # Full-text search vector

    class Meta:
        indexes = [
            models.Index(fields=['search_vector'], name='search_vector_idx')
        ]

# Magazine content model 
class MagazineContent(models.Model):
    magazine_id=models.IntegerField()
    content = models.TextField()
    vector_representation = VectorField(dimensions=384) # Semantic search vector

    class Meta:
        indexes = [
            HnswIndex(
                name="clip_l14_vectors_index",
                fields=["vector_representation"],
                opclasses=["vector_cosine_ops"],
                m=16,
                ef_construction=64,
            )
        ]

        
