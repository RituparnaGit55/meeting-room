from django.urls import path
from . import views

urlpatterns = [
    path("", views.AdminDashboardPageView.as_view(), name="admin-dashboard-page"),
    path("api/stats/", views.DashboardView.as_view(), name="admin-dashboard-api"),
    path("api/user-action/", views.AdminUserActionView.as_view(), name="admin-user-action"),
    path("api/meeting-action/", views.AdminMeetingActionView.as_view(), name="admin-meeting-action"),
    path("export-report/", views.AdminExportReportView.as_view(), name="admin-export-report"),
]
