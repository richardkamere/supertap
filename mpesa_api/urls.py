from . import views
from rest_framework import routers
from django.urls import path, include

urlpatterns = [
    path('online/lipa', views.lipa_na_mpesa_online, name='lipa_na_mpesa'),
    path('c2b/register', views.register_urls, name="register_mpesa_validation"),
    path('c2b/confirmation', views.confirmation, name="confirmation"),
    path('c2b/c2b_confirmation', views.c2b_confirmation, name="c2b_confirmation"),
    path('c2b/validation', views.validation, name="validation"),
    path('c2b/callback', views.call_back, name="call_back"),
    path('check/auto_check_payment', views.auto_check_payment, name="auto_check_payment"),

]
