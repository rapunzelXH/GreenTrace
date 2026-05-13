# GreenTrace — Environmental Procurement Accountability Platform

## Project Structure

```
GreenTrace/
├── manage.py
├── requirements.txt
│
├── config/                         # Django project config
│   ├── settings.py                 # All settings (DRF, JWT, Celery, CORS)
│   ├── urls.py                     # Root URL config
│   ├── celery.py                   # Celery app (Phase 2)
│   └── wsgi.py
│
├── greentrace/                     # Main Django app
│   ├── admin.py                    # Admin panel registrations
│   ├── apps.py                     # Loads signals on startup
│   ├── models/                     # 11 models (Phase 1)
│   │   ├── user.py
│   │   ├── company_profile.py
│   │   ├── project.py
│   │   ├── eco_milestone.py
│   │   ├── tender_application.py
│   │   ├── compliance_evidence.py
│   │   ├── carbon_data.py
│   │   ├── discrepancy_report.py
│   │   ├── project_follow.py
│   │   ├── audit_log.py
│   │   └── extension_request.py
│   └── api/                        # REST API (Phase 1 + 2)
│       ├── permissions.py          # IsAdmin, IsBusiness, IsJournalist
│       ├── serializers.py          # 1 serializer per model
│       ├── views.py                # ViewSets for all models
│       ├── urls.py                 # Router + JWT auth endpoints
│       ├── signals.py              # Eco-Score, AuditLog, RedFlag auto-logic
│       └── tasks.py                # Celery background tasks
│
└── frontend/                       # React frontend (Phase 3)
    ├── package.json
    ├── tailwind.config.js
    └── src/
        ├── App.js                  # Router + role-based routes
        ├── api/
        │   ├── client.js           # Axios + JWT interceptors
        │   └── endpoints.js        # All API functions
        ├── context/
        │   └── AuthContext.js      # Global auth state
        └── pages/
            ├── auth/               # Login, Register
            ├── admin/              # Dashboard, Projects, Milestones, Reports, AuditLog
            ├── business/           # Dashboard, Milestones, CarbonCalculator, TenderApply
            └── journalist/         # Map, ProjectList, ProjectDetail, ReportForm, EcoScoreCompare
```

---

## Backend Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py makemigrations greentrace
python manage.py migrate

# 4. Create admin superuser
python manage.py createsuperuser

# 5. Start Django server
python manage.py runserver
```

Django API runs at: http://127.0.0.1:8000
Admin panel: http://127.0.0.1:8000/admin/
API root: http://127.0.0.1:8000/api/

---

## Frontend Setup

```bash
cd frontend

# Install npm packages
npm install

# Start React dev server
npm start
```

React app runs at: http://localhost:3000

---

## Celery Setup (Phase 2 — background tasks)

Requires Redis running locally.

```bash
# Install Redis (Windows: use WSL or Docker)
# macOS:   brew install redis && redis-server
# Ubuntu:  sudo apt install redis-server && redis-server

# Start Celery worker (in a separate terminal)
celery -A config worker -l info

# Start Celery Beat scheduler (in another terminal)
celery -A config beat -l info
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/auth/register/ | POST | UC-01: Register |
| /api/auth/login/ | POST | UC-02: Login (JWT) |
| /api/auth/logout/ | POST | UC-35: Logout |
| /api/auth/me/ | GET/PUT | UC-03: Profile |
| /api/projects/ | GET/POST | UC-04, UC-15 |
| /api/projects/map/ | GET | UC-15: GeoJSON map |
| /api/milestones/ | GET/POST | UC-05 |
| /api/milestones/{id}/review/ | POST | UC-11, UC-12 |
| /api/applications/ | GET/POST | UC-06 |
| /api/applications/{id}/submit/ | POST | UC-06: Finalise |
| /api/applications/{id}/evaluate/ | POST | UC-07: Admin scores |
| /api/evidence/ | POST | UC-08, UC-09 |
| /api/carbon/ | GET/POST | UC-10 |
| /api/extensions/ | POST | UC-13 |
| /api/extensions/{id}/review/ | POST | UC-14 |
| /api/reports/ | GET/POST | UC-16 |
| /api/reports/{id}/respond/ | POST | UC-16: Admin responds |
| /api/follows/ | GET/POST/DELETE | UC-17 |
| /api/companies/compare/ | POST | UC-18 |
| /api/audit/ | GET | FR-38: Audit log |

---

## User Roles

| Role | Access |
|------|--------|
| ADMIN | Create projects, review milestones, evaluate bids, respond to reports |
| BUSINESS | Apply for tenders, upload evidence, submit carbon data |
| JOURNALIST | View map, follow projects, compare eco-scores, submit reports |

---

## Tech Stack

**Backend:** Django 4.2, Django REST Framework, SimpleJWT, Celery, Redis, Pillow

**Frontend:** React 18, React Router v6, Tailwind CSS, Leaflet.js, Recharts, Axios
