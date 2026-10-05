from django.urls import path
from .views import RegisterAPI,LoginAPI,LogOutAPI

urlpatterns = [
  path("register/",RegisterAPI.as_view(),name='register'),
  path("login/",LoginAPI.as_view(),name='login'),
  path("logout/",LogOutAPI.as_view(),name='logout'),
]