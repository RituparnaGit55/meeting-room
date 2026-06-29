from django.urls import path
from . import views

urlpatterns = [
    path("", views.SummaryListCreateView.as_view(), name="summary-list"),
    path("<int:pk>/", views.SummaryDetailView.as_view(), name="summary-detail"),
    path("meetings/<int:meeting_id>/", views.MeetingSummaryRetrieveView.as_view(), name="meeting-summary"),
    path("meetings/<int:meeting_id>/generate/", views.GenerateSummaryView.as_view(), name="summary-generate"),
    # Meeting Notes (real-time)
    path("meetings/<int:meeting_id>/notes/", views.MeetingNoteListCreateView.as_view(), name="meeting-notes"),
    path("notes/<int:pk>/", views.MeetingNoteDetailView.as_view(), name="meeting-note-detail"),
]
