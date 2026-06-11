# Meeting Collaboration Platform

A comprehensive internal meeting and collaboration platform with video conferencing, AI-powered meeting summaries, and more.

## Features

- User authentication and authorization
- Meeting scheduling and management
- Real-time video conferencing (WebRTC)
- Screen sharing
- Meeting chat
- File sharing
- Recording management
- AI transcription and meeting summaries
- Task management
- YouTube upload automation
- Admin dashboard
- Analytics dashboard

## Tech Stack

### Backend
- Python 3.12
- Django 5+
- Django REST Framework
- Django Channels
- PostgreSQL
- Redis
- Celery
- JWT Authentication

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- Vanilla JavaScript
- WebRTC
- WebSocket

## Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd meeting_sw
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements/development.txt
```

4. Copy environment example file and update variables:
```bash
cp .env.example .env
# Edit .env to set your configuration
```

5. Apply migrations:
```bash
cd src
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Running with Docker

To be added.

## Project Structure

```
meeting_sw/
├── src/
│   ├── config/          # Django project settings
│   ├── apps/            # Django applications
│   │   ├── accounts/    # User management & authentication
│   │   ├── meetings/    # Meeting management
│   │   ├── participants/ # Meeting participants
│   │   ├── chat/        # Meeting chat
│   │   ├── recordings/  # Recording management
│   │   ├── transcripts/ # Meeting transcripts
│   │   ├── summaries/   # Meeting summaries
│   │   ├── tasks/       # Task management
│   │   ├── notifications/ # Notifications
│   │   ├── analytics/   # Analytics
│   │   ├── webhooks/    # Webhooks
│   │   ├── api_keys/    # API keys
│   │   └── dashboard/   # Dashboard
│   ├── static/          # Static files
│   ├── templates/       # HTML templates
│   └── manage.py
├── requirements/        # Project dependencies
├── docker/              # Docker configuration
├── .env.example
├── .gitignore
├── README.md
└── ARCHITECTURE.md
```

## License

To be added.
