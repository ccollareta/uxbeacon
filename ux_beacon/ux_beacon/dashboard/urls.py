from django.urls import path
from .views import dashboard, add_website, collect_heatmap_data

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('add-website/', add_website, name='add_website'),
    path('api/heatmap/', collect_heatmap_data, name='collect_heatmap_data'),
]
