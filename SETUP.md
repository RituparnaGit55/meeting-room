
# Meeting Platform Setup Guide

## Prerequisites
1. **Python 3.10+** - Download from https://www.python.org/downloads/
2. (Optional) **PostgreSQL** and **Redis** for production

---

## Step 1: Install Python
Download Python 3.10 or higher from the link above and install it.
- Make sure to check "Add Python to PATH" during installation!

## Step 2: Install Dependencies
Open a terminal in the `meeting_sw` folder and run:
```bash
pip install -r requirements.txt
```

## Step 3: Apply Database Migrations
```bash
cd src
python manage.py migrate
```

## Step 4: Create a Superuser (optional but recommended)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

## Step 5: Start the Server! 🚀
```bash
python manage.py runserver
```

Now visit **http://localhost:8000/** in your browser!

---

## What's Included
✅ Full Authentication System (Register/Login/Logout, Email Verification, Password Reset)
✅ Meeting Management (Instant, Scheduled, Recurring)
✅ Join via Room Code/Meeting ID (Password Protected)
✅ Meeting Controls (Waiting Room, Raise Hand, Host Controls)
✅ Bootstrap 5 Responsive Templates
✅ RESTful APIs with DRF
✅ Clean Architecture (Services, Repositories)

---

## Admin Panel
Once logged in as superuser, visit: http://localhost:8000/admin/
