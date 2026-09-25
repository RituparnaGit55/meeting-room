from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.accounts.models import User
from apps.meetings.models import Meeting, RestrictedKeyword
from apps.meetings.services import check_text_against_meeting_keywords, has_active_restricted_keywords


class RestrictedKeywordFeatureTestCase(APITestCase):
    client: APIClient  # type: ignore[assignment]

    def setUp(self):
        self.client = APIClient()

        # Create Admin user
        self.admin_user = User.objects.create_superuser(  # type: ignore[call-arg]
            email="admin@example.com",
            password="adminpassword123",
            first_name="Admin",
            last_name="User"
        )
        
        # Create Normal participant user
        self.normal_user = User.objects.create_user(  # type: ignore[call-arg]
            email="user@example.com",
            password="userpassword123",
            first_name="Normal",
            last_name="Participant"
        )
        
        # Create Meeting 1
        self.meeting_1 = Meeting.objects.create(
            title="Meeting 1234",
            host=self.admin_user,
            start_time=timezone.now(),
            duration=60,
            status="IN_PROGRESS"
        )
        
        # Create Meeting 2
        self.meeting_2 = Meeting.objects.create(
            title="Meeting 5678",
            host=self.admin_user,
            start_time=timezone.now(),
            duration=60,
            status="IN_PROGRESS"
        )

    def test_1_create_restriction_as_admin(self):
        """Test 1: Admin can create a restricted keyword for a specific meeting."""
        self.client.force_login(self.admin_user)
        
        url = reverse("admin-keyword-action")
        payload = {
            "action": "create_keyword",
            "meeting_id": self.meeting_1.id,
            "keyword": "phone number",
            "status": "ENABLED"
        }
        
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(RestrictedKeyword.objects.filter(meeting=self.meeting_1, keyword="phone number").exists())

    def test_2_chat_keyword_detection(self):
        """Test 2: Restricted keyword is detected in chat for Meeting 1234."""
        RestrictedKeyword.objects.create(
            meeting=self.meeting_1,
            keyword="phone number",
            status="ENABLED",
            created_by=self.admin_user
        )
        
        # Check text containing restricted phrase
        is_restricted, matched = check_text_against_meeting_keywords(
            self.meeting_1.id,
            "Please send me your phone number."
        )
        self.assertTrue(is_restricted)
        self.assertEqual(matched, "phone number")

    def test_3_meeting_scoping_isolation(self):
        """Test 3: Restricted keyword in Meeting 1234 does NOT trigger in Meeting 5678."""
        RestrictedKeyword.objects.create(
            meeting=self.meeting_1,
            keyword="phone number",
            status="ENABLED",
            created_by=self.admin_user
        )
        
        # Check text in Meeting 2 (Meeting 5678)
        is_restricted, matched = check_text_against_meeting_keywords(
            self.meeting_2.id,
            "Please send me your phone number."
        )
        self.assertFalse(is_restricted)
        self.assertIsNone(matched)

    def test_4_multiple_keywords_detection(self):
        """Test 4: Multiple restricted keywords in Meeting 1234 are both detected."""
        RestrictedKeyword.objects.create(
            meeting=self.meeting_1,
            keyword="phone number",
            status="ENABLED",
            created_by=self.admin_user
        )
        RestrictedKeyword.objects.create(
            meeting=self.meeting_1,
            keyword="mobile number",
            status="ENABLED",
            created_by=self.admin_user
        )
        
        is_restricted_1, matched_1 = check_text_against_meeting_keywords(
            self.meeting_1.id, "Call me on my phone number."
        )
        is_restricted_2, matched_2 = check_text_against_meeting_keywords(
            self.meeting_1.id, "Send your mobile number here."
        )
        
        self.assertTrue(is_restricted_1)
        self.assertEqual(matched_1, "phone number")
        self.assertTrue(is_restricted_2)
        self.assertEqual(matched_2, "mobile number")

    def test_5_disabled_restriction(self):
        """Test 5: Disabled restricted keywords are not enforced."""
        RestrictedKeyword.objects.create(
            meeting=self.meeting_1,
            keyword="phone number",
            status="DISABLED",
            created_by=self.admin_user
        )
        
        is_restricted, matched = check_text_against_meeting_keywords(
            self.meeting_1.id, "Here is my phone number."
        )
        self.assertFalse(is_restricted)
        self.assertIsNone(matched)

    def test_6_delete_restriction(self):
        """Test 6: Deleted restricted keywords are no longer enforced."""
        kw = RestrictedKeyword.objects.create(
            meeting=self.meeting_1,
            keyword="phone number",
            status="ENABLED",
            created_by=self.admin_user
        )
        
        # Delete keyword
        kw.delete()
        
        is_restricted, matched = check_text_against_meeting_keywords(
            self.meeting_1.id, "Here is my phone number."
        )
        self.assertFalse(is_restricted)
        self.assertIsNone(matched)

    def test_7_unauthorized_user_access(self):
        """Test 7: Normal non-admin user cannot perform admin keyword actions."""
        # 1. DRF API check returns 403 Forbidden
        self.client.force_authenticate(user=self.normal_user)  # type: ignore[attr-defined]
        drf_url = reverse("restricted-keyword-list-create")
        drf_response = self.client.post(drf_url, {
            "meeting": self.meeting_1.id,
            "keyword": "unauthorized keyword",
            "status": "ENABLED"
        })
        self.assertEqual(drf_response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 2. Session admin action redirects non-admin user (302)
        self.client.force_login(self.normal_user)
        action_url = reverse("admin-keyword-action")
        payload = {
            "action": "create_keyword",
            "meeting_id": self.meeting_1.id,
            "keyword": "unauthorized keyword",
            "status": "ENABLED"
        }
        action_response = self.client.post(action_url, payload)
        self.assertIn(action_response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_302_FOUND])
        self.assertFalse(RestrictedKeyword.objects.filter(keyword="unauthorized keyword").exists())

    def test_8_existing_functionality(self):
        """Test 8: Verify meeting access and keyword check API endpoints work cleanly."""
        url = reverse("check-text-keyword", kwargs={"meeting_identifier": self.meeting_1.room_code})
        
        # GET request checking if meeting has restrictions
        res_get = self.client.get(url)
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertFalse(getattr(res_get, "data", {}).get("has_restricted_keywords"))  # type: ignore[attr-defined]
        
        # Add restriction
        RestrictedKeyword.objects.create(
            meeting=self.meeting_1,
            keyword="confidential",
            status="ENABLED",
            created_by=self.admin_user
        )
        
        # Check active status
        res_get_active = self.client.get(url)
        self.assertEqual(res_get_active.status_code, status.HTTP_200_OK)
        self.assertTrue(getattr(res_get_active, "data", {}).get("has_restricted_keywords"))  # type: ignore[attr-defined]
        
        # POST check content
        res_post = self.client.post(url, {"content": "This contains confidential info."})
        self.assertEqual(res_post.status_code, status.HTTP_200_OK)
        self.assertTrue(getattr(res_post, "data", {}).get("is_restricted"))  # type: ignore[attr-defined]
        self.assertEqual(getattr(res_post, "data", {}).get("matched_keyword"), "confidential")  # type: ignore[attr-defined]
