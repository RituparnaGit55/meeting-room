import os
from celery import shared_task
from django.conf import settings


@shared_task
def upload_recording_to_youtube(recording_id, recording_model="Recording"):
    """
    Upload a meeting recording to the company YouTube channel.
    Automatically generates title, description, and chapters.
    Default visibility: private.
    
    Pipeline:
    Meeting Ended → Recording Saved → Transcript → Summary → YouTube Upload
    """
    try:
        from apps.recordings.models import Recording
        from apps.meetings.models import MeetingRecording
        from apps.summaries.models import Summary
        from .youtube_service import YouTubeUploadService

        # Get the recording and file path
        if recording_model == "MeetingRecording":
            recording = MeetingRecording.objects.get(id=recording_id)
            file_path = recording.file.path
            meeting = recording.meeting
        else:
            recording = Recording.objects.get(id=recording_id)
            file_path = recording.file_path
            if not os.path.isabs(file_path):
                file_path = os.path.join(str(settings.MEDIA_ROOT), file_path)
            meeting = recording.meeting

        if not os.path.exists(file_path):
            print(f"YouTube upload skipped: File not found at {file_path}")
            return

        # Check if YouTube credentials are configured
        credentials_file = getattr(settings, "YOUTUBE_API_CREDENTIALS_FILE", None)
        if not credentials_file:
            print("YouTube upload skipped: YOUTUBE_API_CREDENTIALS_FILE not configured.")
            return

        # Get summary for description generation
        summary = None
        try:
            summary = Summary.objects.get(meeting=meeting)
        except Summary.DoesNotExist:
            pass

        # Auto-generate title
        date_str = meeting.start_time.strftime("%Y-%m-%d") if meeting.start_time else "Unknown Date"
        title = f"{meeting.title} - {date_str}"

        # Auto-generate description with chapters
        description = YouTubeUploadService.generate_description(meeting, summary)

        # Generate dynamic branded thumbnail
        thumbnail_path = None
        try:
            thumbnail_path = YouTubeUploadService.generate_thumbnail(meeting)
            print(f"Generated thumbnail at {thumbnail_path} for meeting {meeting.id}")
        except Exception as thumb_gen_err:
            print(f"Failed to generate video thumbnail: {thumb_gen_err}")

        # Get visibility setting
        visibility = getattr(settings, "YOUTUBE_DEFAULT_VISIBILITY", "private")

        # Upload to YouTube
        result = YouTubeUploadService.upload_video(
            file_path=file_path,
            title=title,
            description=description,
            visibility=visibility,
            thumbnail_path=thumbnail_path,
        )

        # Cleanup thumbnail file if it exists
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                os.remove(thumbnail_path)
                print(f"Cleaned up temp thumbnail file: {thumbnail_path}")
            except Exception as rm_err:
                print(f"Failed to delete temp thumbnail: {rm_err}")

        if result:
            video_id = result["video_id"]
            video_url = result["video_url"]

            # Save YouTube data to either Recording model
            recording.is_uploaded_to_youtube = True
            recording.youtube_url = video_url
            recording.youtube_video_id = video_id
            recording.youtube_visibility = visibility
            recording.save(update_fields=[
                "is_uploaded_to_youtube", "youtube_url",
                "youtube_video_id", "youtube_visibility"
            ])

            # Notify host: YouTube Upload Complete
            try:
                from apps.notifications.services import NotificationService
                NotificationService.notify_host(
                    meeting=meeting,
                    notification_type="YOUTUBE_UPLOADED",
                    title="Recording Uploaded to YouTube",
                    message=f"The recording for meeting '{meeting.title}' has been uploaded to YouTube: {video_url}",
                )
            except Exception as notify_err:
                print(f"Failed to send YouTube upload notification: {notify_err}")

            print(f"Recording {recording_id} uploaded to YouTube: {video_url}")
        else:
            print(f"YouTube upload failed for recording {recording_id}.")

    except Exception as e:
        print(f"Error uploading recording {recording_id} to YouTube: {e}")
