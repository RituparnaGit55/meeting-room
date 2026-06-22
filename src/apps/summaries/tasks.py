import json
from celery import shared_task
from django.conf import settings
from openai import OpenAI
from apps.meetings.models import Meeting
from apps.transcripts.models import Transcript
from .models import Summary

@shared_task
def generate_meeting_summary(meeting_id):
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        transcripts = Transcript.objects.filter(meeting=meeting).order_by("start_time")
        
        if not transcripts.exists():
            print(f"No transcripts found for meeting {meeting_id}. Cannot generate summary.")
            return

        # Format transcript text
        transcript_lines = []
        for t in transcripts:
            start_fmt = f"{int(t.start_time//60):02d}:{int(t.start_time%60):02d}" if t.start_time else "00:00"
            speaker = t.speaker_label or (t.speaker.get_full_name() if t.speaker else "Unknown Speaker")
            transcript_lines.append(f"{speaker} [{start_fmt}]: {t.text}")
            
        full_transcript = "\n".join(transcript_lines)
        
        if not settings.OPENAI_API_KEY:
            print("OPENAI_API_KEY is missing. Cannot generate summary.")
            return
            
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        system_prompt = """
        You are an AI assistant that analyzes meeting transcripts and generates structured summaries.
        You must output a JSON object containing EXACTLY the following keys:
        - "summary_text": A brief paragraph summarizing the entire meeting.
        - "key_points": A list of strings, each being a key discussion point.
        - "decisions_taken": A list of strings, each being a decision made during the meeting.
        - "action_items": A list of strings, each being an action item or task assigned.
        - "follow_up_tasks": A list of strings, each being a follow-up task.
        - "meeting_notes": Detailed notes covering the meeting comprehensively.
        - "minutes_of_meeting": Formal Minutes of Meeting (MOM) formatted as a string.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please analyze the following transcript and extract the requested information in JSON format:\n\n{full_transcript}"}
            ]
        )
        
        content = response.choices[0].message.content
        parsed_data = json.loads(content)
        
        # Update or create Summary
        Summary.objects.update_or_create(
            meeting=meeting,
            defaults={
                "summary_text": parsed_data.get("summary_text", ""),
                "key_points": parsed_data.get("key_points", []),
                "decisions_taken": parsed_data.get("decisions_taken", []),
                "action_items": parsed_data.get("action_items", []),
                "follow_up_tasks": parsed_data.get("follow_up_tasks", []),
                "meeting_notes": parsed_data.get("meeting_notes", ""),
                "minutes_of_meeting": parsed_data.get("minutes_of_meeting", "")
            }
        )
        
        print(f"Meeting summary generated successfully for meeting {meeting_id}.")
        
    except Exception as e:
        print(f"Error generating meeting summary for meeting {meeting_id}: {e}")
