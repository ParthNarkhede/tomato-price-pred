from django.urls import path
from . import views  # Importing from views.py

urlpatterns = [
    path('predict/', views.price_prediction_view, name='price_prediction'),
]
