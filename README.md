# SkillBridge – Student Skill Exchange & Peer Learning Platform

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0%2B-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**SkillBridge** is a modern, production-grade full-stack web application designed for students to exchange knowledge and learn skills from one another without monetary barriers.

---

## 🌟 Project Overview

SkillBridge enables students to showcase skills they can teach (e.g., Python, React, UI/UX Design, Spanish) and connect with peers who possess skills they want to learn. The platform incorporates request management workflows, peer rating systems, search & multi-facet filtering, protected authentication dashboards, and responsive visual interfaces.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Django 5.x / 6.x
- **Database**: Django ORM with SQLite (local development)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons
- **Static Assets**: WhiteNoise, Gunicorn
- **Configuration**: python-dotenv, Django Security Middleware

---

## 🏗️ Architecture & Database Design

### Models Schema

1. **`accounts.Profile`**
   - Linked `OneToOneField` to Django's built-in `auth.User`.
   - Fields: `bio`, `college_or_organization`, `city`, `preferred_learning_mode` (Online/Offline/Both), `profile_image`, `created_at`, `updated_at`.
   - Automatic creation via Django `post_save` signals.

2. **`skills.Skill`**
   - Global directory of skills categorized into Programming, Web Development, Mobile Development, Data Science, AI, Design, Communication, Languages, and Other.

3. **`skills.UserSkill`**
   - Relationship mapping user profiles to skills with `skill_type` (`TEACH` vs `LEARN`) and `proficiency_level` (`Beginner`, `Intermediate`, `Advanced`).

4. **`exchanges.SkillExchangeRequest`**
   - Tracks peer exchange requests between `sender` and `receiver` with `skill_offered`, `skill_requested`, status state machine (`Pending` -> `Accepted` / `Rejected` -> `Completed` / `Cancelled`), and message logs.

5. **`exchanges.Feedback`**
   - Peer rating system allowing ratings from **1 to 5 stars** and review comments for completed exchanges.

---

## 📁 Project Structure

```
skillbridge/
│
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── build.sh
├── render.yaml
│
├── skillbridge/          # Project Settings & Routing
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/             # User Profiles, Auth, Dashboard, Explore Learners
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── skills/               # Skill Catalog & User Skill Inventory
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── exchanges/            # Skill Exchange Requests & Feedback Ratings
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── templates/            # Django Templates & Inheritance Layouts
│   ├── base.html
│   ├── home.html
│   ├── about.html
│   ├── includes/
│   ├── accounts/
│   ├── skills/
│   └── exchanges/
│
└── static/               # Custom CSS Design System, JS & Assets
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── images/
```

---

## 🚀 Local Installation & Setup

Follow these steps to run SkillBridge locally:

### 1. Clone or Open Project
```bash
cd C:\Users\GADHAVI\.gemini\antigravity\scratch\skillbridge
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 5. Run Database Migrations & Seed Demo Data
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

### 6. Run Development Server
```bash
python manage.py runserver
```
Open your browser at: `http://127.0.0.1:8000/`

---

## 🔑 Pre-Populated Demo Logins

After running `python manage.py seed_data`, you can sign in with any of the following pre-configured demo student accounts:

| Username | Password | Full Name | College / Org | Primary Teaching Skill |
| :--- | :--- | :--- | :--- | :--- |
| **`alex_rivera`** | `password123` | Alex Rivera | Stanford University | Python & Django |
| **`sophia_chen`** | `password123` | Sophia Chen | MIT | UI/UX Design & React |
| **`marcus_johnson`** | `password123` | Marcus Johnson | UC Berkeley | Data Science & Spanish |
| **`priya_patel`** | `password123` | Priya Patel | NYU | Flutter & Public Speaking |
| **`admin`** | `admin123456` | Admin User | Administrator | Django Admin Portal |

---

## 🌐 Free Deployment Guide on Render

SkillBridge is pre-configured for seamless deployment on **Render**:

1. Push your repository to **GitHub**.
2. Log into [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following settings:
   - **Environment**: `Python`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn skillbridge.wsgi:application`
5. Add Environment Variables:
   - `SECRET_KEY`: (Generate a secure random string)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com`
6. Click **Create Web Service**. Render will execute `build.sh` (installing dependencies, collecting static files, applying migrations, and seeding data) and bring your web app online.

---

## 🧪 Testing & Validation

Run the automated test suite covering authentication, signal auto-creation, skill management, and request status state machine:

```bash
python manage.py test
```

---
## Live

https://skillbridge-0my3.onrender.com/


## 🚀 Future Enhancements

- **Real-Time Chat**: WebSockets via Django Channels for live peer messaging.
- **Email Notifications**: Automated email alerts for pending exchange requests and approvals.
- **AI Learner Matching**: Intelligent recommendation engine matching students by complementary skill vectors.
- **Video Session Integration**: Embedded WebRTC / Jitsi video conferencing for remote peer sessions.
