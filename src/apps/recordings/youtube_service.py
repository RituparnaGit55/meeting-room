import os
import json
from django.conf import settings


class YouTubeUploadService:
    """
    Service to upload recordings to a company YouTube channel.
    Uses the YouTube Data API v3 with OAuth2 stored credentials.
    
    Requirements:
    - google-api-python-client
    - google-auth-oauthlib
    - A credentials JSON file set via YOUTUBE_API_CREDENTIALS_FILE in settings
    - A stored token file (auto-generated after first auth)
    """

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    TOKEN_FILE = "youtube_token.json"

    @staticmethod
    def _get_authenticated_service():
        """Build an authenticated YouTube API service."""
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = None
        token_path = os.path.join(settings.BASE_DIR, YouTubeUploadService.TOKEN_FILE)
        credentials_file = getattr(settings, "YOUTUBE_API_CREDENTIALS_FILE", None)

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, YouTubeUploadService.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Do not run run_local_server in background Celery execution to avoid hanging
                raise PermissionError(
                    "YouTube API token file is missing or invalid, and interactive OAuth authorization is disabled "
                    "for non-interactive execution. Please run authentication locally once or provide a valid 'youtube_token.json' file."
                )

        return build("youtube", "v3", credentials=creds)

    @staticmethod
    def generate_chapters_from_transcript(meeting):
        """Generate YouTube chapters string from transcript timestamps."""
        from apps.transcripts.models import Transcript

        transcripts = Transcript.objects.filter(meeting=meeting).order_by("start_time")
        if not transcripts.exists():
            return ""

        chapters = ["00:00 Meeting Start"]
        # Group transcript segments into ~5 minute chunks for chapters
        chunk_interval = 300  # 5 minutes in seconds
        last_chapter_time = 0

        for t in transcripts:
            if t.start_time and (t.start_time - last_chapter_time) >= chunk_interval:
                mins = int(t.start_time // 60)
                secs = int(t.start_time % 60)
                speaker = t.speaker_label or "Speaker"
                # Truncate text for chapter title
                chapter_title = t.text[:60].strip()
                if len(t.text) > 60:
                    chapter_title += "..."
                chapters.append(f"{mins:02d}:{secs:02d} {speaker}: {chapter_title}")
                last_chapter_time = t.start_time

        return "\n".join(chapters)

    @staticmethod
    def generate_description(meeting, summary=None):
        """Auto-generate a YouTube video description from meeting metadata and summary."""
        lines = [
            f"Meeting: {meeting.title}",
            f"Date: {meeting.start_time.strftime('%B %d, %Y') if meeting.start_time else 'N/A'}",
            f"Host: {meeting.host.get_full_name() or meeting.host.email}",
            "",
        ]

        if summary:
            if summary.summary_text:
                lines.append("📋 Summary:")
                lines.append(summary.summary_text)
                lines.append("")
            if summary.key_points:
                lines.append("🔑 Key Points:")
                for point in summary.key_points[:10]:
                    lines.append(f"  • {point}")
                lines.append("")

        # Add chapters
        chapters = YouTubeUploadService.generate_chapters_from_transcript(meeting)
        if chapters:
            lines.append("📌 Chapters:")
            lines.append(chapters)

        return "\n".join(lines)

    @staticmethod
    def generate_thumbnail(meeting):
        """
        Dynamically generate a high-quality video thumbnail using Pillow (PIL).
        Creates a 1280x720 canvas with a premium gradient background and meeting details.
        """
        from PIL import Image, ImageDraw, ImageFont
        import tempfile

        # 1280 x 720 (YouTube Recommended Size)
        width, height = 1280, 720
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)

        # Draw a beautiful gradient background (dark violet to deep indigo/blue)
        for y in range(height):
            factor = y / height
            r = int(30 + (76 - 30) * factor)
            g = int(27 + (29 - 27) * factor)
            b = int(75 + (149 - 75) * factor)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Add decorative premium glow shapes
        draw.ellipse([-200, -200, 400, 400], fill=(45, 30, 85))
        draw.ellipse([1000, 400, 1500, 900], fill=(55, 35, 95))

        # Load fonts - fallback to default if custom fonts aren't available
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 64)
            subtitle_font = ImageFont.truetype("arial.ttf", 36)
            brand_font = ImageFont.truetype("arialbd.ttf", 40)
        except IOError:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()

        # Draw brand header
        draw.text((100, 80), "MeetFlow", fill=(244, 63, 94), font=brand_font)
        draw.text((310, 80), "|   RECORDING", fill=(229, 231, 235), font=subtitle_font)

        # Draw line under header
        draw.line([(100, 150), (1180, 150)], fill=(255, 255, 255), width=2)

        # Draw Meeting Title (wrapped if too long)
        title_text = meeting.title
        if len(title_text) > 40:
            title_text = title_text[:37] + "..."

        draw.text((100, 240), title_text, fill=(255, 255, 255), font=title_font)

        # Host name & Date info
        host_name = meeting.host.get_full_name() or meeting.host.email
        date_str = meeting.start_time.strftime("%B %d, %Y") if meeting.start_time else "Unknown Date"
        time_str = meeting.start_time.strftime("%I:%M %p") if meeting.start_time else ""

        draw.text((100, 420), f"Hosted by: {host_name}", fill=(209, 213, 219), font=subtitle_font)
        draw.text((100, 490), f"Date: {date_str}   {time_str}", fill=(209, 213, 219), font=subtitle_font)

        # Add a premium footer badge
        draw.rectangle([(100, 580), (320, 640)], fill=(99, 102, 241))
        draw.text((120, 592), "INTERNAL", fill=(255, 255, 255), font=subtitle_font)

        # Save to temp file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"meetflow_thumb_{meeting.id}.jpg")
        image.save(temp_path, "JPEG", quality=95)

        return temp_path

    @staticmethod
    def upload_video(
        file_path,
        title,
        description="",
        visibility="private",
        category_id="22",  # 22 = People & Blogs
        thumbnail_path=None,
    ):
        """
        Upload a video to YouTube.
        
        Returns:
            dict with 'video_id' and 'video_url' on success, or None on failure.
        """
        from googleapiclient.http import MediaFileUpload

        if not os.path.exists(file_path):
            print(f"YouTube upload failed: File not found at {file_path}")
            return None

        try:
            youtube = YouTubeUploadService._get_authenticated_service()

            body = {
                "snippet": {
                    "title": title[:100],  # YouTube title max 100 chars
                    "description": description[:5000],  # YouTube desc max 5000 chars
                    "categoryId": category_id,
                    "tags": ["meeting", "recording", "internal"],
                },
                "status": {
                    "privacyStatus": visibility,  # "private", "unlisted", or "public"
                    "selfDeclaredMadeForKids": False,
                },
            }

            media = MediaFileUpload(
                file_path,
                mimetype="video/webm",
                resumable=True,
                chunksize=10 * 1024 * 1024,  # 10MB chunks
            )

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status_obj, response = request.next_chunk()
                if status_obj:
                    print(f"YouTube upload progress: {int(status_obj.progress() * 100)}%")

            video_id = response.get("id")
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # Set thumbnail if specified and generated
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
                    ).execute()
                    print(f"YouTube thumbnail uploaded successfully for video {video_id}")
                except Exception as thumb_err:
                    print(f"Failed to upload YouTube thumbnail: {thumb_err}")

            print(f"YouTube upload successful: {video_url}")
            return {"video_id": video_id, "video_url": video_url}

        except Exception as e:
            print(f"YouTube upload error: {e}")
            return None
