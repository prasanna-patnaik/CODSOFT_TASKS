# Todo List Backend API

A Django REST Framework backend for managing authenticated user todo tasks. The API supports JWT authentication, task CRUD, owner-based permissions, filtering, searching, ordering, pagination, and Swagger/OpenAPI documentation.

## Tech Stack

- Python 3.13
- Django
- Django REST Framework
- SQLite
- SimpleJWT
- django-filter
- drf-spectacular

## Installation Guide

1. Open the project folder:

```bash
cd Task_3_Todo_List_Backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Create a local environment file:

```bash
copy .env.example .env
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Project Architecture

The backend is split into focused Django apps:

- `config`: Project settings, root URLs, ASGI/WSGI entry points, and custom exception handling.
- `accounts`: Registration, login, refresh token, current user, logout, auth serializers, validators, and response utilities.
- `tasks`: Task model, admin registration, serializer, filters, permissions, validators, router, and CRUD viewset.

Authentication uses JWT access and refresh tokens. Task access is scoped by owner, so users can only create, list, read, update, and delete their own tasks.

## Folder Structure

```text
Task_3_Todo_List_Backend/
├── accounts/
│   ├── apps.py
│   ├── serializers.py
│   ├── urls.py
│   ├── utils.py
│   ├── validators.py
│   └── views.py
├── config/
│   ├── asgi.py
│   ├── exceptions.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tasks/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
├── .env.example
├── manage.py
├── postman/
│   └── Todo_List_Backend.postman_collection.json
├── README.md
└── requirements.txt
```

## Authentication Guide

Use the registration or login endpoint to receive tokens:

- `access`: Short-lived token used in the `Authorization` header.
- `refresh`: Token used to request a new access token.

Authenticated requests must include:

```text
Authorization: Bearer <access_token>
```

Logout blacklists the supplied refresh token. After logout, that refresh token cannot be used again.

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | Register a user and receive JWT tokens | No |
| POST | `/api/auth/login/` | Login and receive JWT tokens | No |
| POST | `/api/auth/refresh/` | Refresh access token | No |
| GET | `/api/auth/me/` | Get current authenticated user | Yes |
| POST | `/api/auth/logout/` | Blacklist refresh token | Yes |

### Tasks

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| GET | `/api/tasks/` | List current user's tasks | Yes |
| POST | `/api/tasks/` | Create a task | Yes |
| GET | `/api/tasks/{id}/` | Retrieve a task | Yes |
| PUT | `/api/tasks/{id}/` | Replace a task | Yes |
| PATCH | `/api/tasks/{id}/` | Partially update a task | Yes |
| DELETE | `/api/tasks/{id}/` | Delete a task | Yes |

## Filtering, Searching, Ordering, Pagination

Task list query parameters:

```text
completed=true
priority=high
category=work
search=meeting
ordering=-created_at
page=1
```

Supported filters:

- `completed`
- `priority`
- `category`

Search fields:

- `title`
- `description`

Ordering fields:

- `created_at`
- `updated_at`
- `due_date`
- `priority`

Pagination page size is `10`.

## Example Requests

### Register

```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "jane",
  "email": "jane@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "password": "StrongPass123!",
  "password_confirm": "StrongPass123!"
}
```

### Login

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "jane",
  "password": "StrongPass123!"
}
```

### Create Task

```http
POST /api/tasks/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Finish backend project",
  "description": "Complete documentation and API verification.",
  "completed": false,
  "priority": "high",
  "category": "work",
  "due_date": "2026-07-20T18:00:00Z"
}
```

### List Tasks

```http
GET /api/tasks/?completed=false&priority=high&search=backend&ordering=-created_at&page=1
Authorization: Bearer <access_token>
```

## Example Responses

### Successful Auth Response

```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "username": "jane",
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "date_joined": "2026-07-13T10:00:00Z"
  },
  "tokens": {
    "refresh": "refresh-token",
    "access": "access-token"
  }
}
```

### Task Response

```json
{
  "id": 1,
  "title": "Finish backend project",
  "description": "Complete documentation and API verification.",
  "completed": false,
  "priority": "high",
  "category": "work",
  "due_date": "2026-07-20T18:00:00Z",
  "created_at": "2026-07-13T10:05:00Z",
  "updated_at": "2026-07-13T10:05:00Z",
  "owner": "jane"
}
```

### Paginated Task List Response

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Finish backend project",
      "description": "Complete documentation and API verification.",
      "completed": false,
      "priority": "high",
      "category": "work",
      "due_date": "2026-07-20T18:00:00Z",
      "created_at": "2026-07-13T10:05:00Z",
      "updated_at": "2026-07-13T10:05:00Z",
      "owner": "jane"
    }
  ]
}
```

### Validation Error Response

```json
{
  "title": [
    "Task title cannot be empty."
  ]
}
```

### Unauthorized Response

```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Swagger Guide

After starting the server, open:

```text
http://127.0.0.1:8000/api/docs/
```

Other schema views:

```text
http://127.0.0.1:8000/api/schema/
http://127.0.0.1:8000/api/redoc/
```

To authorize requests in Swagger UI:

1. Register or login to get an access token.
2. Click `Authorize`.
3. Enter:

```text
Bearer <access_token>
```

4. Run authenticated task requests from the Swagger UI.

## Postman

Import:

```text
postman/Todo_List_Backend.postman_collection.json
```

The collection includes variables for `base_url`, `access_token`, `refresh_token`, and `task_id`. Login and registration requests automatically save returned JWT tokens when successful.
