from django.urls import path
from . import views

urlpatterns = [
    path("", views.SummaryListCreateView.as_view(), name="summary-list"),
    path("<int:pk>/", views.SummaryDetailView.as_view(), name="summary-detail"),
    path("meetings/<int:meeting_id>/generate/", views.GenerateSummaryView.as_view(), name="summary-generate"),
]
