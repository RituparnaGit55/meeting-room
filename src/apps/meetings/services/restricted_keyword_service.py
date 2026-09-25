import re
from typing import Tuple, Optional
from apps.meetings.models import Meeting, RestrictedKeyword


def normalize_text(text: str) -> str:
    """
    Normalizes text for keyword comparison:
    - Lowercase
    - Replaces punctuation/dashes with space
    - Collapses multiple whitespace into single space
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def check_text_against_meeting_keywords(meeting_identifier, text: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if `text` contains any ACTIVE (enabled) restricted keywords specifically for the given `meeting_identifier`.
    `meeting_identifier` can be a meeting string ID, room_code, or primary key int.
    
    CRITICAL RULE: Always scopes restrictions strictly to the provided meeting ID.
    Returns: (is_restricted: bool, matched_keyword: str or None)
    """
    if not text or not meeting_identifier:
        return False, None

    normalized_input = normalize_text(text)
    if not normalized_input:
        return False, None

    meeting = None
    if isinstance(meeting_identifier, int) or (isinstance(meeting_identifier, str) and meeting_identifier.isdigit()):
        meeting = Meeting.objects.filter(id=int(meeting_identifier)).first()
    if not meeting and isinstance(meeting_identifier, str):
        meeting = Meeting.objects.filter(meeting_id=meeting_identifier).first() or Meeting.objects.filter(room_code=meeting_identifier).first()

    if not meeting:
        return False, None

    active_keywords = RestrictedKeyword.objects.filter(
        meeting=meeting,
        status="ENABLED"
    ).values_list('keyword', flat=True)

    for raw_keyword in active_keywords:
        normalized_kw = normalize_text(raw_keyword)
        if not normalized_kw:
            continue
        
        pattern = r'\b' + re.escape(normalized_kw) + r'\b'
        if re.search(pattern, normalized_input):
            return True, raw_keyword

    return False, None


def has_active_restricted_keywords(meeting_identifier) -> bool:
    """
    Checks if a meeting has active restricted keywords configured.
    Does NOT reveal the actual restricted keywords to participants.
    """
    if not meeting_identifier:
        return False

    meeting = None
    if isinstance(meeting_identifier, int) or (isinstance(meeting_identifier, str) and meeting_identifier.isdigit()):
        meeting = Meeting.objects.filter(id=int(meeting_identifier)).first()
    if not meeting and isinstance(meeting_identifier, str):
        meeting = Meeting.objects.filter(meeting_id=meeting_identifier).first() or Meeting.objects.filter(room_code=meeting_identifier).first()

    if not meeting:
        return False

    return RestrictedKeyword.objects.filter(meeting=meeting, status="ENABLED").exists()
