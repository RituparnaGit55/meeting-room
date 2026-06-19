
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.MeetingViewSet, basename='meeting')
router.register(r'(?P<meeting_pk>\d+)/participants', views.MeetingParticipantViewSet, basename='meeting-participant')

urlpatterns = [
    path('api/join/', views.JoinMeetingAPIView.as_view(), name='join-meeting-api'),
    path('api/recordings/upload/', views.UploadRecordingView.as_view(), name='upload-recording-api'),
    path('api/', include(router.urls)),

    # Web URLs
    path('dashboard/', views.MeetingDashboardView.as_view(), name='meeting-dashboard'),
    path('create/', views.CreateMeetingView.as_view(), name='create-meeting'),
    path('my-meetings/', views.MyMeetingsView.as_view(), name='my-meetings'),
    path('join/', views.JoinMeetingPageView.as_view(), name='join-meeting-page'),
    path('join/<str:room_code>/', views.JoinMeetingPageView.as_view(), name='join-meeting-page-with-code'),
    path('room/<str:room_code>/', views.MeetingRoomView.as_view(), name='meeting-room'),
]
