from django.urls import path
from . import views

urlpatterns = [
    path("", views.UserNotificationListView.as_view(), name="notification-list"),
    path("<int:pk>/", views.NotificationDetailView.as_view(), name="notification-detail"),
    path("<int:pk>/read/", views.MarkNotificationReadView.as_view(), name="notification-mark-read"),
    path("read-all/", views.MarkAllReadView.as_view(), name="notification-read-all"),
    path("unread-count/", views.UnreadCountView.as_view(), name="notification-unread-count"),
]
