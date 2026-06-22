import os
import assemblyai as aai
from celery import shared_task
from django.conf import settings
from apps.recordings.models import Recording
from apps.meetings.models import MeetingRecording
from .models import Transcript

@shared_task
def process_transcription(recording_id, recording_model="Recording"):
    """
    Process transcription for a meeting recording using AssemblyAI.
    recording_model: 'Recording' (apps.recordings) or 'MeetingRecording' (apps.meetings)
    """
    try:
        if recording_model == "MeetingRecording":
            recording = MeetingRecording.objects.get(id=recording_id)
            file_path = recording.file.path
            meeting = recording.meeting
        else:
            recording = Recording.objects.get(id=recording_id)
            # Handle if file_path is relative or absolute
            file_path = recording.file_path
            if not os.path.isabs(file_path):
                file_path = os.path.join(settings.MEDIA_ROOT, file_path)
            meeting = recording.meeting
            
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
            
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
        if not aai.settings.api_key:
            print("AssemblyAI API Key is not set in settings.")
            return
            
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            language_detection=True  # Automatically detects English, Hindi, etc.
        )
        
        transcriber = aai.Transcriber(config=config)
        print(f"Starting transcription for {file_path}")
        transcript = transcriber.transcribe(file_path)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"Transcription failed: {transcript.error}")
            return
            
        # Create transcripts from utterances
        created_count = 0
        for utterance in transcript.utterances:
            Transcript.objects.create(
                meeting=meeting,
                speaker_label=f"Speaker {utterance.speaker}", # e.g. "Speaker A"
                text=utterance.text,
                start_time=utterance.start / 1000.0, # convert ms to seconds
                end_time=utterance.end / 1000.0
            )
            created_count += 1
            
        print(f"Transcription completed for recording {recording_id}. Created {created_count} utterances.")
        
        # Trigger meeting summary generation automatically
        from apps.summaries.tasks import generate_meeting_summary
        generate_meeting_summary.delay(meeting.id)
        
    except Exception as e:
        print(f"Error processing transcription: {e}")
