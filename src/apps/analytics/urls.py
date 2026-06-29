from django.urls import path
from . import views

urlpatterns = [
    path("meeting-analytics/", views.MeetingAnalyticsListCreateView.as_view(), name="meeting-analytics-list"),
    path("meeting-analytics/<int:pk>/", views.MeetingAnalyticsDetailView.as_view(), name="meeting-analytics-detail"),
    path("user-analytics/", views.UserAnalyticsListCreateView.as_view(), name="user-analytics-list"),
    path("user-analytics/<int:pk>/", views.UserAnalyticsDetailView.as_view(), name="user-analytics-detail"),
    
    # Statistical Endpoints
    path("meetings/", views.MeetingStatisticsView.as_view(), name="meeting-statistics"),
    path("attendance/", views.AttendanceStatisticsView.as_view(), name="attendance-statistics"),
    path("recordings/", views.RecordingStatisticsView.as_view(), name="recording-statistics"),
]
