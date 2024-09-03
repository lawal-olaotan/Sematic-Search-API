from django.urls import path
from .views import MagazineSearchAPIView

urlpatterns = [
    path('', MagazineSearchAPIView.as_view(), name='search'),
]