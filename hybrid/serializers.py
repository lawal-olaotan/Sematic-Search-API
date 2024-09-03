# serializers.py
from rest_framework import serializers
from .models import MagazineInformation, MagazineContent

class MagazineInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MagazineInformation
        fields = ['id', 'title', 'author', 'publication_date', 'category', 'publication_country', 'revenue_generated', 'content']

class MagazineContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MagazineContent
        fields = ['id', 'magazine_id', 'content', 'vector_representation']
