from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('messages/', views.MessageListCreateView.as_view(), name='message-list'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('messages/upload/', views.MessageFileUploadView.as_view(), name='message-upload'),
]
