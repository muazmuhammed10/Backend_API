# Backend API Authorization

A practical FastAPI backend project focused on REST APIs, MySQL, authentication, and authorization.

## Features

- FastAPI REST API
- MySQL + SQLAlchemy
- User registration and login
- Bcrypt password hashing
- JWT authentication
- Protected routes
- User/Admin role-based authorization
- Swagger API documentation

## Technologies

Python • FastAPI • SQLAlchemy • MySQL • JWT • Bcrypt • Pydantic • Uvicorn

## Main Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/register` | Register user |
| POST | `/login` | Login and get JWT |
| GET | `/users/me` | Get logged-in user |
| GET | `/users` | Get users |
| GET | `/users/{id}` | Get user |
| PUT | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |
| GET | `/admin` | Admin-only dashboard |

## Run

```bash
venv\Scripts\Activate.ps1
uvicorn main:app --reload