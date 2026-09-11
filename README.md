# Meeting Room Platform

A modern, full-stack real-time meeting and collaboration platform engineered with **Django 5**, **Django REST Framework**, **Django Channels (WebSockets)**, **WebRTC**, and AI-assisted transcriptions and summaries.

Designed as a final-year engineering project, **Meeting Room Platform** delivers peer-to-peer video conferencing, real-time messaging, meeting scheduling, automated AI processing, role-based dashboards, and webhook integrations.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Authentication & Authorization](#authentication--authorization)
- [Meeting Room & Video Features](#meeting-room--video-features)
- [Scheduling & Task Management](#scheduling--task-management)
- [AI Transcriptions & Summaries](#ai-transcriptions--summaries)
- [Security Features](#security-features)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Directory Structure](#project-directory-structure)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Project Overview

**Meeting Room Platform** provides enterprise-style virtual meeting spaces directly in the browser without third-party plugins. Users can schedule upcoming meetings, start instant rooms, participate in multi-user WebRTC video calls, chat in real-time, upload meeting recordings, generate AI-powered text summaries, and track assigned action items via integrated dashboards.

---

## Key Features

- 🎥 **Real-time WebRTC Video Conferencing**: Low-latency video/audio streaming with peer mesh connection negotiation via WebSockets.
- 💻 **Screen Sharing & In-Meeting Chat**: Instant display sharing and live text chat during active sessions.
- 🔐 **Dual Authentication System**: Support for JWT-authenticated API access, session-based browser logins, and Google OAuth2 integration.
- 📅 **Meeting Management**: Schedule future meetings with auto-generated unique room codes, passcodes, and duration tracking.
- 🤖 **AI-Powered Meeting Processing**: Automated speech-to-text transcription (AssemblyAI integration) and meeting summarization (OpenAI integration).
- 📹 **Recording Management**: Secure recording upload handling and optional YouTube video hosting automation.
- 📊 **Role-Based Dashboards**: User dashboard for meeting history and custom Admin dashboard for platform metrics.
- 🔔 **Real-Time Notifications & Webhooks**: Live alert triggers and outgoing webhook event signatures for external service integrations.

---

## System Architecture

```
                      +---------------------------------------+
                      |           Web Client (Browser)         |
                      |   HTML5 / CSS3 / JavaScript / WebRTC  |
                      +-------------------+-------------------+
                                          |
                        HTTP / REST       |    WebSocket (WS/WSS)
                                          |
                      +-------------------v-------------------+
                      |      Daphne / Django ASGI Server      |
                      +-------------------+-------------------+
                                          |
           +------------------------------+------------------------------+
           |                                                             |
+----------v----------+                                       +----------v----------+
|  Django REST API /  |                                       |   Django Channels   |
|   Web Application   |                                       | (WebRTC Signaling / |
+----------+----------+                                       |   In-Meeting Chat)  |
           |                                                  +----------+----------+
           |                                                             |
+----------v-------------------------------------------------------------v----------+
|                                Database & Background Layer                         |
|   PostgreSQL / SQLite (Database)   |   Redis (Channels & Celery Task Queue)        |
+------------------------------------------------------------------------------------+
```

---

## Technology Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: Django 5.x, Django REST Framework (DRF)
- **Real-Time Signaling**: Django Channels 4.x, Daphne (ASGI)
- **Database**: PostgreSQL / SQLite (via `dj-database-url`)
- **Task Queue & Caching**: Celery, Redis
- **Security & Tokens**: `djangorestframework-simplejwt`, `django-allauth`, `python-dotenv`

### Frontend
- **Interface**: HTML5, Vanilla JavaScript (ES6+), Bootstrap 5, Custom CSS
- **Protocols**: WebRTC API (`RTCPeerConnection`, `RTCDataChannel`), WebSocket API

### AI & Media Integration
- **Speech Recognition**: AssemblyAI API
- **NLP & Summarization**: OpenAI API
- **Video Storage / CDN**: AWS S3 (`django-storages`), YouTube Data API v3

---

## Authentication & Authorization

- **User Registration & Login**: Traditional email/password workflow with password hashing and optional email verification.
- **JWT Token Authentication**: Access and refresh tokens (`/api/v1/auth/login/`, `/api/v1/auth/refresh/`) with automatic token rotation and blacklist enforcement.
- **Google OAuth2**: OAuth integration powered by `django-allauth` for one-click user login.
- **Role Control**: Fine-grained access control distinguishing standard users (`USER`) from system administrators (`ADMIN`).

---

## Meeting Room & Video Features

1. **Room Creation**: Instant room generation or custom scheduled slots with room codes.
2. **WebRTC Peer Connections**: Direct P2P audio/video feed stream exchange via WebSocket signaling channels (`ws/meetings/<room_code>/`).
3. **Screen Sharing**: Dynamic canvas track insertion (`getDisplayMedia`).
4. **Live Chat**: Room-scoped text broadcast saved to meeting history.

---

## Scheduling & Task Management

- **Scheduled Meetings**: Reserve future rooms, invite participants by email, and enforce start/end window rules.
- **Action Items**: Extract and assign tasks during or post-meeting with priority levels, deadlines, and completion statuses.

---

## Security Features

- 🛡️ **Environment Variable Isolation**: Zero hardcoded API keys or passwords; configuration managed cleanly via `.env`.
- 🔐 **CSRF Protection & SameSite Cookies**: Django CSRF middleware enabled with configured origins for development and production (`CSRF_TRUSTED_ORIGINS`).
- ⚡ **Secure Proxy SSL Handling**: HTTPS proxy header resolution (`SECURE_PROXY_SSL_HEADER`) configured for deployment environments like Vercel.
- 🔒 **Database Integrity**: Strictly parameterised queries ORM layer preventing SQL injection attacks.

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Git

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/RituparnaGit55/meeting-room.git
   cd meeting-room
   ```

2. **Set Up Python Environment**:
   ```bash
   # Windows:
   py -m venv venv
   venv\Scripts\activate

   # Linux/macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment File**:
   ```bash
   cp .env.example .env
   # Edit .env with your specific database/API credentials if needed
   ```

5. **Apply Database Migrations**:
   ```bash
   py src/manage.py migrate
   ```

6. **Create Admin User**:
   ```bash
   py create_test_user.py
   # Default Admin Credentials: Username: admin | Password: admin123
   ```

---

## Environment Variables

Refer to [.env.example](.env.example) for all available keys:

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Toggle debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed host names | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostgreSQL / DB string | `sqlite:///db.sqlite3` |
| `GOOGLE_CLIENT_ID` | OAuth Client ID | `your-google-client-id` |
| `GOOGLE_CLIENT_SECRET` | OAuth Secret Key | `your-google-client-secret` |
| `OPENAI_API_KEY` | OpenAI API key for summaries | `your-openai-api-key` |
| `ASSEMBLYAI_API_KEY` | Speech-to-text API key | `your-assemblyai-key` |

---

## Running the Application

### Option 1: Development Server Script (Recommended)
```bash
py run_meetflow.py
```
*Access the application at `http://127.0.0.1:8001/`*

### Option 2: Standard Django Command
```bash
cd src
py manage.py runserver 127.0.0.1:8000
```
*Access the application at `http://127.0.0.1:8000/`*

---

## Testing

Run unit tests and verification scripts:

```bash
# Run Django test suite
py src/manage.py test

# Run Webhook integration tests
py test_webhooks.py

# Run API payload validation tests
py test_invalid_payloads.py
```

---

## Deployment

The platform includes full serverless configuration for **Vercel** (`vercel.json`, `api/index.py`) and standard WSGI/ASGI entrypoints (`src/config/wsgi.py`, `src/config/asgi.py`) for containerized or Linux VPS deployment (Gunicorn / Daphne / Nginx).

---

## Project Directory Structure

```
meeting-room/
├── api/                      # Serverless deployment adapter (Vercel)
│   └── index.py
├── requirements/             # Environment-specific dependencies
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── src/                      # Main Django Application Core
│   ├── apps/
│   │   ├── accounts/         # Authentication & User Management
│   │   ├── meetings/         # Meeting Management & WebRTC views
│   │   ├── chat/             # Meeting Chat Consumers & Models
│   │   ├── recordings/       # Video Recording Upload & Processing
│   │   ├── transcripts/      # AssemblyAI Transcription Processing
│   │   ├── summaries/        # OpenAI Summary Generation
│   │   ├── tasks/            # Action Item Tracking
│   │   ├── notifications/    # In-App Notifications
│   │   ├── analytics/        # Platform & Meeting Metrics
│   │   ├── webhooks/         # Event Webhook Delivery
│   │   └── dashboard/        # Admin & User Dashboards
│   ├── config/               # Project Settings, URLs, ASGI & WSGI
│   ├── static/               # CSS, JS, Images, Icons
│   ├── templates/            # HTML Templates (Bootstrap 5)
│   └── manage.py
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusion rules
├── LICENSE                   # Open-source MIT License
├── README.md                 # Project Documentation
├── run_meetflow.py           # Helper script to run dev server
├── test_webhooks.py          # Webhook verification test suite
└── test_invalid_payloads.py  # API payload validation test suite
```

---

## Future Enhancements

- 🌐 **SFU (Selective Forwarding Unit) Integration**: Transition from Mesh WebRTC to Mediasoup/Janus SFU for large scale meetings (100+ users).
- 🎙️ **Live Captions**: Real-time streaming subtitles over WebSocket during meetings.
- 📅 **Calendar Integrations**: Bi-directional sync with Google Calendar and Outlook Calendar.

---

## License

This project is licensed under the [MIT License](LICENSE).
