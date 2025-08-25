# Drilling Campaign Management System

A modern system for managing drilling campaigns, tasks, rigs, and wells.

## Architecture Overview

This application follows a layered architecture pattern with the following components:

1. **Presentation Layer**: FastAPI RESTful API
2. **Business Logic Layer**: Service modules implementing business rules
3. **Data Access Layer**: SQLAlchemy ORM with PostgreSQL database
4. **Authentication Layer**: JWT-based authentication and authorization

## Directory Structure

```
src/
├── api/              # API endpoints
├── auth/             # Authentication and authorization
├── database/         # Database models and connection
├── models/           # Pydantic models for validation
├── services/         # Business logic services
└── main.py          # Application entry point
```

## Features

- User management with role-based access control
- Campaign management with wells and rigs
- Task management with status tracking and comments
- Dashboard with KPIs and alerts
- File attachments for tasks
- Audit logging for all changes

## Requirements

- Python 3.8+
- PostgreSQL database
- Dependencies listed in `requirements.txt`

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost/drilling_db
   export SECRET_KEY=your-secret-key-here
   ```

3. Run the application:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Documentation

- Interactive docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## Database Schema

The application uses PostgreSQL with the following tables:
- users
- user_roles
- campaigns
- rigs
- wells
- tasks
- task_comments
- attachments
- audit_logs

## Authentication

The API uses JWT tokens for authentication. To access protected endpoints:

1. Create a user account
2. Log in to receive an access token
3. Include the token in the Authorization header:
   ```
   Authorization: Bearer <your-token>
   ```

## Role-Based Access Control

The system supports the following roles:
- admin: Full access to all features
- ops_manager: Manage campaigns, wells, rigs, and tasks
- engineer: Create/update tasks, view campaigns
- logistics: Manage equipment and logistics data
- executive: Read-only access to dashboard and reports