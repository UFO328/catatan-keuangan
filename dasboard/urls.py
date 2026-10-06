from django.urls import path 
from .views import DashboardMoneyTracker

urlpatterns = [
  path("dashboard/",DashboardMoneyTracker.as_view(),name="dasboard")
]