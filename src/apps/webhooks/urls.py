from django.urls import path
from . import views

urlpatterns = [
    path("", views.WebhookListCreateView.as_view(), name="webhook-list-create"),
    path("<int:pk>/", views.WebhookDetailView.as_view(), name="webhook-detail"),
    path("<int:pk>/test/", views.TestWebhookView.as_view(), name="webhook-test"),
]
