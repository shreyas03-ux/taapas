from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('record/', views.record_screen, name='record_screen'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
]

