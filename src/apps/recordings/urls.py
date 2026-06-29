from django.urls import path
from . import views

urlpatterns = [
    path("", views.RecordingListCreateView.as_view(), name="recording-list"),
    path("<int:pk>/", views.RecordingDetailView.as_view(), name="recording-detail"),
    path("meetings/<int:meeting_id>/start/", views.StartRecordingView.as_view(), name="start-recording"),
    path("meetings/<int:meeting_id>/stop/", views.StopRecordingView.as_view(), name="stop-recording"),
    path("meetings/<int:meeting_id>/url/", views.GetRecordingURLView.as_view(), name="get-recording-url"),
]
