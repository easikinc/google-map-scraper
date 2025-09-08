from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('results/', views.results, name='results'),
    path('download_csv/', views.download_csv, name='download_csv'),
]

