from django.contrib import admin
from .models import MagazineInformation, MagazineContent

@admin.register(MagazineInformation)
class MagazineInformationAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_date', 'category', 'publication_country', 'revenue_generated')
    search_fields = ('title', 'author','content')

@admin.register(MagazineContent)
class MagazineContentAdmin(admin.ModelAdmin):
    list_display = ('magazine_id', 'content', 'vector_representation')
    search_fields = ('content',)
