# Smart Task Management System

Production-quality mini product built with Flask, PostgreSQL, REST APIs, Flask-Login authentication, Pandas/NumPy analytics, and Flask-SocketIO real-time updates.

---

## Tech Stack

- Python
- Flask
- PostgreSQL
- Flask-SQLAlchemy
- Flask-Login
- Flask-SocketIO
- Pandas
- NumPy
- HTML, CSS, Bootstrap 5
- REST APIs

---

## Features

- **Authentication**
  - User registration
  - User login
  - User logout
  - Password hashing with `generate_password_hash` / `check_password_hash`
- **Task Management**
  - Add task
  - Update task
  - Delete task
  - View all tasks (user-specific)
- **Task Fields**
  - Title
  - Description
  - Priority
  - Status
  - Created Date
- **Analytics Dashboard (Pandas + NumPy)**
  - Total tasks
  - Completed tasks
  - Pending tasks
  - Completion percentage
- **WebSocket Real-Time Updates**
  - Live event updates on task create/update/delete
- **Frontend**
  - Responsive Bootstrap UI
  - Analytics cards
  - Task form
  - Task table
  - Priority and status badges

---

## Project Structure

```text
smart_task_management_system/
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── dashboard.html
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── task_routes.py
│   │   └── analytics_routes.py
│   │
│   ├── models/
│   │   ├── user_model.py
│   │   └── task_model.py
│   │
│   ├── sockets/
│   │   └── socket_events.py
│   │
│   ├── utils/
│   │   └── analytics.py
│   │
│   ├── config.py
│   └── __init__.py
│
├── requirements.txt
├── run.py
├── schema.sql
├── README.md
└── .env
```

---

## Database Design

### Database Name

`task_management_db`

### Tables

- **users**
  - `id` (PK)
  - `username` (unique)
  - `email` (unique)
  - `password`
- **tasks**
  - `id` (PK)
  - `title`
  - `description`
  - `priority`
  - `status`
  - `created_date`
  - `user_id` (FK -> `users.id`, cascade delete)

You can initialize schema using `schema.sql`.

---

## Setup Instructions

### 1) Clone and enter project

```bash
git clone <your-repo-url>
cd smart_task_management_system
```

### 2) Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Create PostgreSQL database

```bash
createdb task_management_db
```

### 5) Configure environment

Update `.env`:

```env
SECRET_KEY=your-very-strong-secret-key
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/task_management_db
SOCKETIO_ASYNC_MODE=threading
```

### 6) (Optional) Apply SQL schema manually

```bash
psql -d task_management_db -f schema.sql
```

> Note: SQLAlchemy also creates tables automatically when app starts.

### 7) Run application

```bash
python run.py
```

Open:
- App: `http://127.0.0.1:5000`
- Login: `http://127.0.0.1:5000/login`
- Register: `http://127.0.0.1:5000/register`
- Dashboard: `http://127.0.0.1:5000/dashboard`

---

## API Endpoints

All task and analytics APIs require login session.

### Task APIs

- `GET /api/tasks` - Fetch all tasks for logged-in user
- `POST /api/tasks` - Create task
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

### Analytics API

- `GET /api/analytics` - Fetch analytics summary

---

## API Testing Instructions

Use Postman or cURL.

### A) Login first (session auth)

1. Register user from UI (`/register`) or use existing account.
2. Login from UI (`/login`).
3. Use the same browser session for API testing, or configure Postman cookie jar after login.

### B) Sample JSON Payloads

Create Task (`POST /api/tasks`)

```json
{
  "title": "Prepare assignment demo",
  "description": "Finalize testing and screenshots",
  "priority": "High",
  "status": "Pending"
}
```

Update Task (`PUT /api/tasks/1`)

```json
{
  "title": "Prepare assignment demo v2",
  "status": "In Progress"
}
```

### C) Expected responses

- Success responses include:
  - `success: true`
  - `message` (for create/update/delete)
  - `task` or `tasks` data
- Error responses include:
  - `success: false`
  - `message` with clear reason

---

## Real-Time Events (Socket.IO)

Dashboard listens to:

- `socket_connected`
- `task_event`

`task_event` is emitted when a task is:
- created
- updated
- deleted

Room-based events are user-scoped (`user_<id>`), so each user receives only their own updates.

---

## Commands Reference

### Run project

```bash
python run.py
```

### Syntax check

```bash
python3 -m compileall app run.py
```

### Reinstall dependencies

```bash
pip install -r requirements.txt
```

---

## Sample Screenshots (for Assignment Report)

Capture and include these screenshots in your submission:

1. **Register Page**
   - Filled registration form
2. **Login Page**
   - Successful login state
3. **Dashboard Overview**
   - Analytics cards visible
4. **Task CRUD**
   - Task created in table
   - Task updated
   - Task deleted
5. **Real-Time Update**
   - Dashboard real-time status changed after CRUD action
6. **API Testing**
   - Postman/cURL responses for all REST endpoints

Suggested naming:
- `01-register.png`
- `02-login.png`
- `03-dashboard.png`
- `04-task-create.png`
- `05-task-update.png`
- `06-task-delete.png`
- `07-api-testing.png`

---

## GitHub Push Commands

```bash
git init
git add .
git commit -m "Build smart task management system with auth, REST APIs, analytics, and real-time updates"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

If repo already exists:

```bash
git add .
git commit -m "Update project modules and documentation"
git push
```

---

## Deployment Guidance

### Recommended Platform Options

- Render
- Railway
- Fly.io
- Any VPS with Gunicorn + Nginx

### Production Checklist

- Set secure `SECRET_KEY`
- Use production PostgreSQL URL
- Set `SESSION_COOKIE_SECURE=true` behind HTTPS
- Set Flask environment to production
- Use process manager (e.g., Gunicorn) in production
- Add logging and monitoring

### Example (Gunicorn)

Install:

```bash
pip install gunicorn
```

Run:

```bash
gunicorn -w 2 -b 0.0.0.0:5000 run:app
```

> For advanced production Socket.IO scaling (WebSocket-heavy workloads), use an async worker stack and add its required dependencies (for example gevent/eventlet-based setup) as per your hosting platform.

---

## Evaluation Notes

This project follows:

- Clean modular architecture (Blueprints, models, utils, sockets)
- Professional code organization
- User-scoped data security
- REST API validation + error handling
- Data analytics with real Pandas/NumPy operations
- Real-time dashboard updates with Flask-SocketIO
