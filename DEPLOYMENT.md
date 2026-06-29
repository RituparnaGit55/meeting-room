# MeetFlow Deployment Documentation

This guide describes how to configure, set up, and deploy the MeetFlow platform in production environments.

---

## 📋 System Prerequisites

Ensure the deployment target environment has the following installed:
1. **Python**: Python 3.10 or higher
2. **Database**: PostgreSQL (recommended for production) or SQLite (default for development)
3. **Message Broker**: Redis (required for Django Channels and Celery tasks)

---

## 🛠️ Step-by-Step Deployment Setup

### 1. Clone & Setup Directory
Clone the repository and create a virtual environment:
```bash
git clone <repository-url>
cd meeting_sw
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a production `.env` file in the root directory:
```ini
# Django core settings
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,127.0.0.1

# Database Configuration
DATABASE_URL=postgres://user:password@localhost:5432/meetflow

# API Integration Credentials
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
OPENAI_API_KEY=your_openai_api_key

# YouTube API OAuth Integration
YOUTUBE_API_CREDENTIALS_FILE=/path/to/client_secrets.json
YOUTUBE_DEFAULT_VISIBILITY=private
```

### 3. Database Initialization
Run Django migration commands to initialize tables and schemas:
```bash
cd src
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Collect Static Files
Gather all static resources for production hosting:
```bash
python manage.py collectstatic --noinput
```

### 5. Running background tasks & workers
Celery is used to execute background transcription and summary workflows asynchronously. Launch Celery worker in the background:
```bash
celery -A config worker --loglevel=info
```

### 6. Process Managers (Gunicorn & Daphne)
In production, run Daphne to support ASGI websockets and Channels traffic:
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```
Use a service supervisor (like systemd) to run Daphne and Celery as persistent background daemons.
