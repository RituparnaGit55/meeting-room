from django.urls import path
from . import views

urlpatterns = [
    path('', views.TranscriptListCreateView.as_view(), name='transcript-list'),
    path('<int:pk>/', views.TranscriptDetailView.as_view(), name='transcript-detail'),
    path('meetings/<int:meeting_id>/', views.MeetingTranscriptListView.as_view(), name='meeting-transcripts'),
    path('meetings/<int:meeting_id>/generate/', views.GenerateTranscriptView.as_view(), name='generate-transcript'),
]
