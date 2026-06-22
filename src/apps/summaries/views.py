from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Summary
from .serializers import SummarySerializer


class SummaryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer
    queryset = Summary.objects.all()


class SummaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer
    queryset = Summary.objects.all()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import generate_meeting_summary

class GenerateSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        # Trigger the celery task
        generate_meeting_summary.delay(meeting_id)
        return Response(
            {"message": "Summary generation triggered successfully."}, 
            status=status.HTTP_202_ACCEPTED
        )
