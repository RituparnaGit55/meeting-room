from django.urls import path
from . import views

urlpatterns = [
    path("", views.TaskListCreateView.as_view(), name="task-list"),
    path("<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"),
    path("meeting/<int:meeting_id>/", views.MeetingTaskListView.as_view(), name="meeting-tasks"),
]
