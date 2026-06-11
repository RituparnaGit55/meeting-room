from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Webhook
from .serializers import WebhookSerializer


class WebhookListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WebhookSerializer
    queryset = Webhook.objects.all()


class WebhookDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WebhookSerializer
    queryset = Webhook.objects.all()
