# MeetFlow API Documentation

This document provides a comprehensive list of all backend REST API endpoints available in the MeetFlow platform.

---

## 🔐 Authentication APIs

### 1. Register User
- **Endpoint**: `POST /api/v1/auth/register/`
- **Description**: Registers a new user.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
- **Response**: `201 Created`

### 2. Login User
- **Endpoint**: `POST /api/v1/auth/token/`
- **Description**: Obtains JWT Access & Refresh tokens.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response**:
  ```json
  {
    "access": "jwt_access_token_here",
    "refresh": "jwt_refresh_token_here"
  }
  ```

---

## 📅 Meeting APIs

### 1. List & Create Meetings
- **Endpoint**: `GET /api/v1/meetings/` / `POST /api/v1/meetings/`
- **Description**: Returns all meetings for the user or schedules a new meeting.
- **Request Body (Create)**:
  ```json
  {
    "title": "Weekly Sync",
    "description": "Team synchronization",
    "meeting_type": "SCHEDULED",
    "start_time": "2026-06-25T10:00:00Z",
    "duration": 45
  }
  ```

### 2. Join Meeting
- **Endpoint**: `POST /api/v1/meetings/api/join/`
- **Description**: Join a meeting by room code.
- **Request Body**:
  ```json
  {
    "room_code": "A1B2C3D4E5"
  }
  ```

---

## 📹 Recording APIs

### 1. Start Recording
- **Endpoint**: `POST /api/v1/recordings/meetings/<int:meeting_id>/start/`
- **Description**: Starts recording for an active meeting.
- **Response**: `200 OK`

### 2. Stop Recording
- **Endpoint**: `POST /api/v1/recordings/meetings/<int:meeting_id>/stop/`
- **Description**: Stops recording for a meeting.
- **Response**: `200 OK`

### 3. Get Recording URL
- **Endpoint**: `GET /api/v1/recordings/meetings/<int:meeting_id>/url/`
- **Description**: Returns local file paths, media URLs, and YouTube status (including URL and video ID) for all recordings attached to the meeting.

---

## 🎙️ AI Transcription APIs

### 1. Generate Transcript
- **Endpoint**: `POST /api/v1/transcripts/meetings/<int:meeting_id>/generate/`
- **Description**: Triggers AssemblyAI speech-to-text processing for all meeting recordings.
- **Response**: `202 Accepted`

### 2. Get Transcript
- **Endpoint**: `GET /api/v1/transcripts/meetings/<int:meeting_id>/`
- **Description**: Fetches all transcribed utterances/segments for the meeting.

---

## 📋 AI Summary APIs

### 1. Generate Summary
- **Endpoint**: `POST /api/v1/summaries/meetings/<int:meeting_id>/generate/`
- **Description**: Triggers OpenAI GPT analysis on meeting transcripts to create summary, decisions, and action items.
- **Response**: `202 Accepted`

### 2. Get Summary
- **Endpoint**: `GET /api/v1/summaries/meetings/<int:meeting_id>/`
- **Description**: Returns summary, key points, decisions, and follow-up tasks.

---

## 📊 Analytics & Control Statistics APIs

### 1. Meeting Statistics
- **Endpoint**: `GET /api/v1/analytics/meetings/`
- **Description**: Returns meeting count, type distribution, status breakdown, and duration averages.

### 2. Attendance Statistics
- **Endpoint**: `GET /api/v1/analytics/attendance/`
- **Description**: Returns average participant attendance, roles distribution, and waiting room entry counts.

### 3. Recording Statistics
- **Endpoint**: `GET /api/v1/analytics/recordings/`
- **Description**: Returns total recording file sizes, formats breakdown, and YouTube upload rates.
