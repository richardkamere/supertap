from . import views
from rest_framework import permissions,routers
from django.urls import path, include


routers = routers.DefaultRouter()
routers.register(r'users', views.UserViewSet)
routers.register(r'access/token', views.getAccessToken, basename="token")


urlpatterns = [
    path('access/token', views.getAccessToken, name='get_mpesa_access_token'),
    path('online/lipa', views.lipa_na_mpesa_online, name='lipa_na_mpesa'),

    path('c2b/register', views.register_urls, name="register_mpesa_validation"),
    path('c2b/confirmation', views.confirmation, name="confirmation"),
    path('c2b/validation', views.validation, name="validation"),
    path('c2b/callback', views.call_back, name="call_back"),
    path('check/auto_check_payment', views.auto_check_payment, name="auto_check_payment"),
    path('', include(routers.urls))

]