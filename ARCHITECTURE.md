# Internal Meeting & Collaboration Platform - Architecture Documentation

## 1. System Architecture Overview

### 1.1 High-Level Architecture

The platform follows a **clean, layered architecture** with the following key components:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Web    │  │  Mobile  │  │   Admin  │  │ Analytics│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                       │
│           (Nginx/Traefik - Load Balancing & Routing)         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Application Layer                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              Django Web Application                    │ │
│  │  - REST API (DRF)                                      │ │
│  │  - WebSocket Consumers (Django Channels)               │ │
│  │  - Service Layer                                       │ │
│  │  - Repository Layer                                    │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  PostgreSQL   │    │     Redis     │    │    Celery     │
│   (Database)  │    │   (Cache/WS)  │    │   (Workers)   │
└───────────────┘    └───────────────┘    └───────────────┘
                              │                     │
                              ▼                     ▼
                    ┌───────────────┐    ┌───────────────┐
                    │  WebRTC Media │    │  AI Services  │
                    │    Server     │    │ (Transcribe,  │
                    └───────────────┘    │   Summarize)  │
                                         └───────────────┘
```

### 1.2 Architectural Principles

- **SOLID Principles**: All code follows SOLID design principles
- **Clean Architecture**: Separation of concerns across layers
- **Service Layer Pattern**: Business logic isolated in service classes
- **Repository Pattern**: Data access abstracted behind repositories
- **Scalability**: Horizontal scaling for all stateless components

---

## 2. Django Project & App Structure

### 2.1 Complete Folder Structure

```
meeting_platform/
├── docker/
│   ├── nginx/
│   │   └── nginx.conf
│   ├── django/
│   │   └── Dockerfile
│   ├── celery/
│   │   └── Dockerfile
│   ├── postgres/
│   │   └── Dockerfile
│   └── redis/
│       └── Dockerfile
├── src/
│   ├── config/                  # Django project config
│   │   ├── __init__.py
│   │   ├── settings/            # Settings per environment
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── staging.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   ├── wsgi.py
│   │   └── routing.py
│   ├── apps/
│   │   ├── core/                # Core utilities & base classes
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── users/               # User & authentication
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── meetings/            # Meeting rooms & scheduling
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── media/               # WebRTC, audio, video
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── chat/                # Meeting chat
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── files/               # File sharing
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── recordings/          # Recording management
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── ai/                  # AI transcription, summaries
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── tasks/               # Task generation & management
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── integrations/        # YouTube, other integrations
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   ├── analytics/           # Analytics & reporting
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── consumers/
│   │   │   ├── tasks/
│   │   │   ├── utils/
│   │   │   ├── exceptions/
│   │   │   └── tests/
│   │   └── admin_dashboard/     # Admin features
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── models.py
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── serializers.py
│   │       ├── services/
│   │       ├── repositories/
│   │       ├── consumers/
│   │       ├── tasks/
│   │       ├── utils/
│   │       ├── exceptions/
│   │       └── tests/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   ├── staging.txt
│   │   └── production.txt
│   └── manage.py
├── logs/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## 3. Database Schema (ERD)

### 3.1 Core Entities

```
┌─────────────────┐       ┌─────────────────┐
│     User        │       │    Department   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ id (PK)         │
│ email           │       │ name            │
│ password        │       │ description     │
│ first_name      │       │ created_at      │
│ last_name       │       │ updated_at      │
│ department_id   │       └─────────────────┘
│ role            │
│ is_active       │
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         │ 1
         │
         │ N
┌─────────────────┐
│   Meeting       │
├─────────────────┤
│ id (PK)         │
│ title           │
│ description     │
│ host_id (FK)    │
│ room_code       │
│ start_time      │
│ end_time        │
│ status          │
│ is_recording    │
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         │ 1
         │
         │ N
┌─────────────────┐       ┌─────────────────┐
│ MeetingParticip │       │   ChatMessage   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ id (PK)         │
│ meeting_id (FK) │       │ meeting_id (FK) │
│ user_id (FK)    │       │ user_id (FK)    │
│ joined_at       │       │ content         │
│ left_at         │       │ timestamp       │
│ is_screen_sharing│      └─────────────────┘
└─────────────────┘
         │
         │ 1
         │
         │ N
┌─────────────────┐       ┌─────────────────┐
│   FileUpload    │       │   Recording     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ meeting_id (FK) │       │ meeting_id (FK) │
│ user_id (FK)    │       │ file_path       │
│ file_name       │       │ duration        │
│ file_path       │       │ created_at      │
│ file_size       │       │ updated_at      │
│ uploaded_at     │       └─────────────────┘
└─────────────────┘
         │
         │ 1
         │
         │ N
┌─────────────────┐       ┌─────────────────┐
│   Transcription │       │ MeetingSummary  │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ meeting_id (FK) │       │ meeting_id (FK) │
│ text            │       │ summary_text    │
│ speaker         │       │ key_points      │
│ timestamp       │       │ action_items    │
│ created_at      │       │ created_at      │
└─────────────────┘       └─────────────────┘
         │
         │ 1
         │
         │ N
┌─────────────────┐
│   MeetingTask   │
├─────────────────┤
│ id (PK)         │
│ meeting_id (FK) │
│ assignee_id (FK)│
│ title           │
│ description     │
│ due_date        │
│ status          │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

---

## 4. API Architecture & Endpoints

### 4.1 API Design Principles

- RESTful API design
- Versioned endpoints (`/api/v1/`)
- JSON request/response format
- JWT authentication (access + refresh tokens)
- Pagination for list endpoints
- Consistent error responses

### 4.2 API Endpoint List

#### 4.2.1 Authentication (`/api/v1/auth/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register/` | User registration |
| POST | `/login/` | User login (get access/refresh tokens) |
| POST | `/refresh/` | Refresh access token |
| POST | `/logout/` | Logout user |
| GET | `/me/` | Get current user profile |
| PUT | `/me/` | Update current user profile |

#### 4.2.2 Users (`/api/v1/users/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all users (admin only) |
| GET | `/{id}/` | Get user details |
| PUT | `/{id}/` | Update user (admin only) |
| DELETE | `/{id}/` | Delete user (admin only) |

#### 4.2.3 Meetings (`/api/v1/meetings/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all meetings |
| POST | `/` | Create new meeting |
| GET | `/{id}/` | Get meeting details |
| PUT | `/{id}/` | Update meeting |
| DELETE | `/{id}/` | Delete meeting |
| POST | `/{id}/join/` | Join a meeting |
| POST | `/{id}/leave/` | Leave a meeting |
| POST | `/{id}/start-recording/` | Start recording |
| POST | `/{id}/stop-recording/` | Stop recording |

#### 4.2.4 Chat (`/api/v1/meetings/{meeting_id}/chat/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List chat messages |
| POST | `/` | Send chat message |

#### 4.2.5 Files (`/api/v1/meetings/{meeting_id}/files/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List uploaded files |
| POST | `/` | Upload file |
| GET | `/{id}/` | Download file |
| DELETE | `/{id}/` | Delete file |

#### 4.2.6 Recordings (`/api/v1/recordings/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List recordings |
| GET | `/{id}/` | Get recording details |
| GET | `/{id}/download/` | Download recording |
| DELETE | `/{id}/` | Delete recording |

#### 4.2.7 AI (`/api/v1/meetings/{meeting_id}/ai/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transcriptions/` | Get transcriptions |
| GET | `/summary/` | Get meeting summary |
| POST | `/generate-summary/` | Generate summary |

#### 4.2.8 Tasks (`/api/v1/tasks/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List tasks |
| POST | `/` | Create task |
| GET | `/{id}/` | Get task details |
| PUT | `/{id}/` | Update task |
| DELETE | `/{id}/` | Delete task |

#### 4.2.9 Analytics (`/api/v1/analytics/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Get analytics dashboard data |
| GET | `/meetings/` | Get meeting analytics |
| GET | `/users/` | Get user activity analytics |

---

## 5. Service Layer & Repository Pattern

### 5.1 Repository Pattern

Each app has a `repositories/` directory containing repository classes that abstract database operations:

```python
# Example: apps/users/repositories/user_repository.py
class UserRepository:
    def get_by_id(self, user_id):
        pass

    def get_by_email(self, email):
        pass

    def create(self, data):
        pass

    def update(self, user, data):
        pass

    def delete(self, user):
        pass
```

### 5.2 Service Layer

Each app has a `services/` directory containing service classes that implement business logic:

```python
# Example: apps/users/services/user_service.py
class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register_user(self, data):
        pass

    def authenticate_user(self, email, password):
        pass

    def update_profile(self, user, data):
        pass
```

---

## 6. Celery & WebSocket Architecture

### 6.1 Celery Architecture

- **Broker**: Redis
- **Backend**: Redis (for task results)
- **Workers**: Multiple workers for different task queues

**Celery Tasks**:
- `process_transcription()` - Process audio for transcription
- `generate_meeting_summary()` - Generate AI summary
- `upload_to_youtube()` - Upload recording to YouTube
- `cleanup_old_recordings()` - Clean up old files
- `send_meeting_reminders()` - Send email reminders

### 6.2 WebSocket Architecture (Django Channels)

**WebSocket Consumers**:
- `MeetingConsumer` - Handles real-time meeting events
- `ChatConsumer` - Handles real-time chat
- `SignalingConsumer` - WebRTC signaling

**Channel Layers**: Redis as channel layer backend

---

## 7. Security, Deployment & Docker Architecture

### 7.1 Security Architecture

- **Authentication**: JWT with access/refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: TLS 1.3 for all traffic
- **Password Hashing**: Argon2 (Django default)
- **CORS**: Strict CORS policy
- **Rate Limiting**: Django REST Framework throttling
- **File Security**: Virus scanning, size limits, type restrictions

### 7.2 Deployment Architecture

- **Web Servers**: Nginx (reverse proxy, load balancer)
- **Application Servers**: Gunicorn + Uvicorn (for ASGI/WebSockets)
- **Database**: PostgreSQL (primary + read replicas)
- **Cache**: Redis cluster
- **Celery**: Multiple worker nodes
- **Media Storage**: S3/GCS compatible object storage
- **CI/CD**: GitHub Actions / GitLab CI

### 7.3 Docker Architecture

**Services in docker-compose.yml**:
- `postgres`: PostgreSQL database
- `redis`: Redis cache/channel layer
- `django`: Django web application
- `celery_worker`: Celery worker
- `celery_beat`: Celery beat scheduler
- `nginx`: Nginx reverse proxy

---

## 8. Development Roadmap

### Phase 1: Core Infrastructure (Weeks 1-2)
- [ ] Project setup & configuration
- [ ] Database schema & migrations
- [ ] User authentication & authorization
- [ ] Core repository & service layer base classes

### Phase 2: Meeting Management (Weeks 3-4)
- [ ] Meeting creation & scheduling
- [ ] Meeting rooms & participant management
- [ ] Basic API endpoints

### Phase 3: Real-time Features (Weeks 5-6)
- [ ] WebSocket consumers
- [ ] Chat functionality
- [ ] WebRTC integration
- [ ] Audio/video conferencing

### Phase 4: Media & Files (Weeks 7-8)
- [ ] Screen sharing
- [ ] File sharing
- [ ] Recording management

### Phase 5: AI Features (Weeks 9-10)
- [ ] Audio transcription
- [ ] Meeting summarization
- [ ] Task generation

### Phase 6: Integrations & Analytics (Weeks 11-12)
- [ ] YouTube upload
- [ ] Admin dashboard
- [ ] Analytics dashboard

### Phase 7: Testing & Deployment (Weeks 13-14)
- [ ] Unit & integration tests
- [ ] Performance testing
- [ ] Docker setup
- [ ] Deployment to staging/production

---

## 9. Architecture Explanation Summary

This architecture is designed with:
- **Scalability**: Stateless application servers, Redis for caching, PostgreSQL with read replicas
- **Maintainability**: Clean architecture, service layer, repository pattern
- **Reliability**: Celery for async tasks, Redis for WebSockets, proper error handling
- **Security**: JWT auth, RBAC, encryption, rate limiting
- **Extensibility**: Modular app structure, easy to add new features
