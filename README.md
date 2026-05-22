# Smart Task Management System

A beautiful, premium, and feature-rich full-stack Task Management System designed as an internship assignment. This application features a robust Python Flask backend, PostgreSQL relational database, real-time WebSocket notifications, a clean interactive Bootstrap-based Kanban dashboard, and data-driven task analytics powered by Pandas and NumPy.

---

## 🚀 Key Features

*   **Secure Authentication**: Dynamic user registration, encrypted credential validation (via `werkzeug.security`), and session-based state management (via Flask-Login).
*   **Task CRUD REST APIs**: Full CREATE, READ, UPDATE, and DELETE operations, fully validated and protected behind authentication.
*   **PostgreSQL Integration**: High-performance persistent database schema mapping user-to-task relationships (One-to-Many).
*   **Analytics Module (Pandas & NumPy)**: Deep workload metrics calculations, including:
    *   Total, Completed, Pending, and In-Progress task counts.
    *   Task Completion Percentage.
    *   Workload Stress Level / Backlog Intensity Scores calculated using priority weightings.
*   **Real-time Synchronization (Flask-SocketIO)**: Live UI updates via WebSockets when tasks are created, updated, or deleted, avoiding page refreshes.
*   **Premium Responsive UI**: Sleek glassmorphism theme, custom interactive CSS cards, and Kanban state boards built on top of Bootstrap.
*   **Automated Testing Suite**: Full suite of 13 integration tests for authentication, task CRUD, error validation, and data analytics.

---

## 📁 Project Architecture & Folder Structure

The project adopts a clean, modular **Flask App Factory Pattern** separating database access, business rules, routes, and interfaces.

```text
Smart_Task_Management_System/
├── app/
│   ├── __init__.py          # Flask App Factory (blueprints, extensions config)
│   ├── config.py            # Development, Testing, Production configurations
│   ├── extensions.py        # Shared instance declarations (DB, LoginManager, SocketIO, Migrate)
│   ├── models/
│   │   ├── __init__.py      # Imports models for registration
│   │   ├── user.py          # User DB Schema & credential helper
│   │   └── task.py          # Task DB Schema & JSON serialization
│   ├── routes/
│   │   ├── __init__.py      # Routing package definition
│   │   ├── auth.py          # Authentication page views & APIs
│   │   └── tasks.py         # Dashboard views & Task REST APIs
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py  # User authentication business logic
│   │   ├── task_service.py  # Task CRUD database service
│   │   └── analytics_service.py # Pandas & NumPy computation engine
│   └── templates/           # Server-side HTML page templates
│       ├── base.html        # Shared head details & scripts
│       ├── auth/            # Register / Login pages
│       └── tasks/           # Dashboard / Analytics pages
├── static/                  # Client-side static resource files
│   ├── css/
│   │   └── style.css        # Custom premium style system overrides
│   └── js/
│       └── app.js           # Client API handler & WebSocket listener
├── tests/                   # Automated Unit & Integration Testing Suite
│   ├── __init__.py
│   ├── test_auth.py         # Registration & login tests
│   └── test_tasks.py        # CRUD & analytics tests
├── .env.example             # Template for configuration settings
├── .env                     # Local secrets and config (git-ignored)
├── .gitignore               # Standard file system clean rules
├── requirements.txt         # Package dependencies
├── schema.sql               # Reference SQL script for PostgreSQL tables
├── create_tables.py         # Script to initialize database tables
└── run.py                   # Application start point
```

---

## 🛠️ Step-by-Step Setup & Installation

### 1. Prerequisite Installations
*   Ensure **Python 3.10+** is installed on your computer.
*   Ensure **PostgreSQL 14+** is installed, configured, and running.

### 2. Configure Environment Variables
Copy `.env.example` into a new file named `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your PostgreSQL credentials and server settings:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=use_your_own_custom_random_secret_string

# Format: postgresql://username:password@localhost:5432/database_name
# If your password contains special characters (like @), url-encode them (e.g. @ becomes %40)
DATABASE_URL=postgresql://postgres:your_postgres_password@localhost:5432/smart_task_db

PORT=5000
HOST=127.0.0.1
```

### 3. Initialize Database Tables
Run the database initializer script to connect to your PostgreSQL database instance and create the matching table structures:
```powershell
.\venv\Scripts\python.exe create_tables.py
```
*(You will see a success output: `Database tables successfully created!`)*

---

## 🕹️ Running the Application

To start the application with real-time Socket.IO polling support:
```powershell
.\venv\Scripts\python.exe run.py
```

Open your browser and navigate to **`http://127.0.0.1:5000`**.
*   Register a new user account.
*   Login to access your personalized Task Dashboard.
*   Add, update, or delete tasks in real-time.
*   Navigate to the Analytics page to view your workload intensity computed via Pandas and NumPy.

---

## 🧪 Running the Testing Suite

Run all unit and integration tests using Python's test runner:
```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests
```

test
