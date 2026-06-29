from django.urls import path
from . import views

urlpatterns = [
    path("", views.AdminDashboardPageView.as_view(), name="admin-dashboard-page"),
    path("api/stats/", views.DashboardView.as_view(), name="admin-dashboard-api"),
]
