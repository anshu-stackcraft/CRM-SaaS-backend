# DegitalStepIn CRM Backend

Django + Django REST Framework backend for DegitalStepIn CRM.

## Features

- JWT authentication (`login`, `refresh`, `profile`)
- Role-based user flow (`super_admin`, `technical_admin`, `employee`)
- Protected APIs for clients, leads, deals, tasks
- Dashboard summary API
- Django Admin configured for user/client/lead/task/deal management
- Health endpoint: `/api/health/`

## Tech Stack

- Python 3.14
- Django 5.x
- Django REST Framework
- SimpleJWT
- SQLite (default)

## Setup

1. Go to backend directory:

```bash
cd backend
```

2. Create virtual environment:

```bash
python -m venv venv
```

3. Activate venv (Windows PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

4. Install dependencies:

```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers pandas
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create superuser:

```bash
python manage.py createsuperuser
```

7. Start server:

```bash
python manage.py runserver
```

Backend runs at: `http://127.0.0.1:8000/`

## Core API Endpoints

### Health

- `GET /api/health/`

### Auth & Users

- `POST /api/users/login/`
- `POST /api/users/refresh/`
- `GET /api/users/profile/`
- `GET /api/users/dashboard-summary/`
- `POST /api/users/register/` (protected, role controlled)
- `GET /api/users/` (protected)

### CRM Modules

- `GET/POST /api/clients/`
- `GET/POST /api/leads/`
- `GET/POST /api/deals/`
- `GET/POST /api/tasks/`

## Role Rules

- `super_admin`: full access + can create `technical_admin` and `employee`
- `technical_admin`: can create `employee`
- `employee`: cannot create users; limited data view for assigned records

## Admin Panel

Open: `http://127.0.0.1:8000/admin/`

Use superuser credentials to manage:

- Users/Auth data
- Clients
- Leads
- Tasks
- Deals

## Useful Commands

```bash
python manage.py check
python manage.py test
```
