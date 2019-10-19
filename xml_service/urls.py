from django.urls import path
from . import views

urlpatterns = [
    path('',views.scrap_data,name='scrap_data')
]
