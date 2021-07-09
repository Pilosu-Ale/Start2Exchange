from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('profit/', views.profitPage, name="profit"),
    path('my_profile/', views.myProfile, name="my_profile"),
]