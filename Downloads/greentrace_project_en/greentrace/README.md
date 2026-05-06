# GreenTrace — Setup Instructions

## Project Structure

```
greentrace/
├── manage.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── greentrace/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    └── models/
        ├── __init__.py
        ├── user.py
        ├── company_profile.py
        ├── project.py
        ├── eco_milestone.py
        ├── tender_application.py
        ├── compliance_evidence.py
        ├── carbon_data.py
        ├── discrepancy_report.py
        ├── project_follow.py
        ├── audit_log.py
        └── extension_request.py
```

## Installation

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create database tables
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser for /admin/
python manage.py createsuperuser

# 5. Start the server
python manage.py runserver
```

## Open the admin panel

Go to: http://127.0.0.1:8000/admin/

## Common errors

**"AUTH_USER_MODEL refers to model that has not been installed"**
-> Check that INSTALLED_APPS in settings.py contains "greentrace".

**Admin does not open / 500 error**
-> Make sure you have run migrate after every makemigrations.

**"no such table"**
-> Run python manage.py migrate again.
