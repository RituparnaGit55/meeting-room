import os
import sys
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Force sys.stdout UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Setup Django Environment
project_dir = Path(__file__).parent
src_dir = project_dir / "src"
sys.path.insert(0, str(src_dir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

from django.utils import timezone
from apps.accounts.models import User
from apps.meetings.models import Meeting, MeetingParticipant
from apps.meetings.services import MeetingService, MeetingParticipantService
from apps.recordings.models import Recording
from apps.transcripts.models import Transcript
from apps.summaries.models import Summary
from apps.webhooks.models import Webhook
from apps.webhooks.services import WebhookService

# Global storage for received webhooks
received_webhooks = []

class WebhookReceiverHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            data = json.loads(body)
            received_webhooks.append(data)
            print(f"  [RECEIVER] Received Webhook Event: {data.get('event')}")
        except Exception as e:
            print(f"  [RECEIVER ERROR] Invalid payload received: {e}")
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))

    def log_message(self, format, *args):
        return

def run_test_server(server):
    server.serve_forever()

def main():
    print("=" * 75)
    print("TESTING ALL WEBHOOK EVENTS: PARTICIPANTS, YOUTUBE UPLOAD, MEETING, RECORDING & TRANSCRIPT")
    print("=" * 75)

    # 1. Start HTTP Receiver on port 8888
    server_address = ('127.0.0.1', 8888)
    httpd = HTTPServer(server_address, WebhookReceiverHandler)
    receiver_url = "http://127.0.0.1:8888/webhook-receiver"
    
    server_thread = threading.Thread(target=run_test_server, args=(httpd,), daemon=True)
    server_thread.start()
    print(f"[STEP 1] Started local Webhook Receiver Server at {receiver_url}")

    # 2. Get or create test users (Host and Participant)
    host_user, _ = User.objects.get_or_create(
        email="webhook_host@example.com",
        defaults={"first_name": "Host", "last_name": "User", "is_active": True}
    )
    participant_user, _ = User.objects.get_or_create(
        email="webhook_participant@example.com",
        defaults={"first_name": "Participant", "last_name": "Member", "is_active": True}
    )

    # Clear previous webhooks for host user
    Webhook.objects.filter(user=host_user).delete()

    # 3. Create Webhook subscriptions for all event choices (including dot-notation forms)
    events_to_register = [
        "MEETING_CREATED", "MEETING_STARTED", "MEETING_ENDED",
        "participants.joined", "participants.left",
        "RECORDING_COMPLETED", "TRANSCRIPT_COMPLETED",
        "SUMMARY_COMPLETED", "youtube.upload.completed"
    ]
    for event in events_to_register:
        Webhook.objects.create(
            user=host_user,
            url=receiver_url,
            event=event,
            is_active=True
        )
    print(f"[STEP 2] Registered active webhooks for user '{host_user.email}' -> Events: {events_to_register}")

    # 4. Action 1: Create Scheduled Meeting (Triggers MEETING_CREATED)
    print("\n[ACTION 1] Creating Scheduled Meeting...")
    meeting = MeetingService.create_scheduled_meeting(
        title="Sprint Sync & Review",
        start_time=timezone.now() + timezone.timedelta(hours=1),
        host=host_user
    )
    print(f"  -> Created Meeting (ID: {meeting.meeting_id}, Room: {meeting.room_code})")
    time.sleep(0.8)

    # 5. Action 2: Host joins meeting (Triggers MEETING_STARTED & PARTICIPANT_JOINED)
    print("\n[ACTION 2] Host Joining Meeting...")
    meeting_obj, host_part = MeetingService.join_meeting_by_room_code(
        room_code=meeting.room_code,
        user=host_user
    )
    print(f"  -> Host joined meeting (Status: {meeting_obj.status})")
    time.sleep(0.8)

    # 6. Action 3: Participant joins meeting (Triggers PARTICIPANT_JOINED)
    print("\n[ACTION 3] Team Member Joining Meeting...")
    _, member_part = MeetingService.join_meeting_by_room_code(
        room_code=meeting.room_code,
        user=participant_user
    )
    print(f"  -> Member '{participant_user.email}' joined meeting")
    time.sleep(0.8)

    # 7. Action 4: Member leaves meeting (Triggers PARTICIPANT_LEFT)
    print("\n[ACTION 4] Team Member Leaving Meeting...")
    MeetingService.leave_meeting(member_part)
    print(f"  -> Member '{participant_user.email}' left meeting")
    time.sleep(0.8)

    # 8. Action 5: Recording Created Event (Triggers RECORDING_COMPLETED)
    print("\n[ACTION 5] Creating Recording Instance...")
    rec = Recording.objects.create(
        meeting=meeting,
        file_path="recordings/sprint_sync.mp4",
        duration=1800
    )
    print(f"  -> Created Recording (ID: {rec.id})")
    time.sleep(0.8)

    # 9. Action 6: YouTube Upload Completed Event (Triggers YOUTUBE_UPLOAD_COMPLETED)
    print("\n[ACTION 6] Dispatching YouTube Upload Completed Event...")
    WebhookService.notify_youtube_upload_completed(
        rec,
        video_url="https://youtube.com/watch?v=demo_video_id_123",
        video_id="demo_video_id_123"
    )
    print(f"  -> Dispatched YouTube Upload Completed Event")
    time.sleep(0.8)

    # 10. Action 7: Transcript Completed Event (Triggers TRANSCRIPT_COMPLETED)
    print("\n[ACTION 7] Creating Transcript & Dispatching Event...")
    t1 = Transcript.objects.create(
        meeting=meeting,
        speaker_label="Speaker A",
        text="Hello team, welcome to the sprint sync.",
        start_time=0.0,
        end_time=3.5
    )
    WebhookService.notify_transcript_completed(meeting, utterance_count=1)
    print(f"  -> Dispatched Transcript Completed Event")
    time.sleep(0.8)

    # 11. Action 8: Summary Completed Event (Triggers SUMMARY_COMPLETED)
    print("\n[ACTION 8] Creating Summary & Dispatching Event...")
    summary_obj = Summary.objects.create(
        meeting=meeting,
        summary_text="Sprint review meeting covering feature progress and next milestones.",
        key_points=["Sprint goals 90% completed"],
        decisions_taken=["Deploy feature flag"],
        action_items=["Complete QA tests"]
    )
    WebhookService.notify_summary_completed(meeting, summary_obj)
    print(f"  -> Dispatched Summary Completed Event")
    time.sleep(0.8)

    # 12. Action 9: Host leaves meeting (Triggers MEETING_ENDED)
    print("\n[ACTION 9] Host Ending Meeting...")
    MeetingService.leave_meeting(host_part)
    meeting.refresh_from_db()
    print(f"  -> Meeting Ended (Status: {meeting.status})")
    time.sleep(0.8)

    # 13. Verify Received Webhooks
    print("\n" + "=" * 75)
    print("VERIFYING DELIVERED WEBHOOK EVENT PAYLOADS")
    print("=" * 75)

    event_counts = {}
    for hook in received_webhooks:
        evt = hook.get("event")
        event_counts[evt] = event_counts.get(evt, 0) + 1
        payload = hook.get("payload", {})
        print(f"[DELIVERED EVENT] {evt}")
        print(f"   Timestamp : {hook.get('timestamp')}")
        print(f"   Payload   : Meeting ID={payload.get('meeting_id')}, Title='{payload.get('title')}'")
        if "participant_name" in payload:
            print(f"               Participant: {payload.get('participant_name')} ({payload.get('role')})")
        if "video_url" in payload:
            print(f"               YouTube Video URL: {payload.get('video_url')}")
        print("-" * 50)

    # Clean shutdown of test server
    httpd.shutdown()

    # Validation Checks
    created_ok = event_counts.get("MEETING_CREATED", 0) >= 1
    started_ok = event_counts.get("MEETING_STARTED", 0) >= 1
    ended_ok = event_counts.get("MEETING_ENDED", 0) >= 1
    joined_ok = event_counts.get("PARTICIPANT_JOINED", 0) >= 2 or event_counts.get("participants.joined", 0) >= 2
    left_ok = event_counts.get("PARTICIPANT_LEFT", 0) >= 1 or event_counts.get("participants.left", 0) >= 1
    youtube_ok = event_counts.get("YOUTUBE_UPLOAD_COMPLETED", 0) >= 1 or event_counts.get("youtube.upload.completed", 0) >= 1
    rec_ok = event_counts.get("RECORDING_COMPLETED", 0) >= 1 or event_counts.get("RECORDING_READY", 0) >= 1
    trans_ok = event_counts.get("TRANSCRIPT_COMPLETED", 0) >= 1 or event_counts.get("TRANSCRIPT_READY", 0) >= 1
    sum_ok = event_counts.get("SUMMARY_COMPLETED", 0) >= 1 or event_counts.get("SUMMARY_READY", 0) >= 1

    print("\n" + "=" * 75)
    print("ALL WEBHOOK EVENTS COMPREHENSIVE TEST SUMMARY")
    print("=" * 75)
    print(f"  - MEETING_CREATED          Events Received : {event_counts.get('MEETING_CREATED', 0)} [{'PASS' if created_ok else 'FAIL'}]")
    print(f"  - MEETING_STARTED          Events Received : {event_counts.get('MEETING_STARTED', 0)} [{'PASS' if started_ok else 'FAIL'}]")
    print(f"  - MEETING_ENDED            Events Received : {event_counts.get('MEETING_ENDED', 0)} [{'PASS' if ended_ok else 'FAIL'}]")
    print(f"  - PARTICIPANT_JOINED       Events Received : {event_counts.get('PARTICIPANT_JOINED', 0) + event_counts.get('participants.joined', 0)} [{'PASS' if joined_ok else 'FAIL'}]")
    print(f"  - PARTICIPANT_LEFT         Events Received : {event_counts.get('PARTICIPANT_LEFT', 0) + event_counts.get('participants.left', 0)} [{'PASS' if left_ok else 'FAIL'}]")
    print(f"  - YOUTUBE_UPLOAD_COMPLETED Events Received : {event_counts.get('YOUTUBE_UPLOAD_COMPLETED', 0) + event_counts.get('youtube.upload.completed', 0)} [{'PASS' if youtube_ok else 'FAIL'}]")
    print(f"  - RECORDING_COMPLETED      Events Received : {event_counts.get('RECORDING_COMPLETED', 0)} [{'PASS' if rec_ok else 'FAIL'}]")
    print(f"  - TRANSCRIPT_COMPLETED     Events Received : {event_counts.get('TRANSCRIPT_COMPLETED', 0)} [{'PASS' if trans_ok else 'FAIL'}]")
    print(f"  - SUMMARY_COMPLETED        Events Received : {event_counts.get('SUMMARY_COMPLETED', 0)} [{'PASS' if sum_ok else 'FAIL'}]")

    all_passed = created_ok and started_ok and ended_ok and joined_ok and left_ok and youtube_ok and rec_ok and trans_ok and sum_ok
    if all_passed:
        print("\n🎉 ALL WEBHOOK FEATURES (YOUTUBE UPLOAD, PARTICIPANTS, MEETING, RECORDING & TRANSCRIPTS) WORKING PERFECTLY!")
    else:
        print("\n❌ SOME WEBHOOK EVENTS FAILED VERIFICATION.")

if __name__ == "__main__":
    main()
