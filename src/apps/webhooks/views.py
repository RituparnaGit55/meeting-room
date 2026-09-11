from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Webhook
from .serializers import WebhookSerializer
from .services import WebhookService


class WebhookListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WebhookSerializer

    def get_queryset(self):
        return Webhook.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WebhookDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WebhookSerializer

    def get_queryset(self):
        return Webhook.objects.filter(user=self.request.user)


class TestWebhookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            webhook = Webhook.objects.get(pk=pk, user=request.user)
            WebhookService.dispatch_event(
                event_type=webhook.event,
                payload={
                    "test": True,
                    "message": f"Test webhook payload for {webhook.event}",
                    "user_id": request.user.id
                },
                user=request.user
            )
            return Response({"message": f"Test event '{webhook.event}' dispatched to {webhook.url}"}, status=status.HTTP_200_OK)
        except Webhook.DoesNotExist:
            return Response({"error": "Webhook not found"}, status=status.HTTP_404_NOT_FOUND)
