# Doctor-Patient Management API

A FastAPI backend for authentication, doctor management, patient management, and doctor-patient assignments.

## Features

- JWT authentication
- Secure password hashing with `pwdlib`
- Admin and doctor roles
- Doctor creation, listing, filtering, updating, and soft deletion
- Patient creation and listing
- Doctor-patient assignment
- SQLite persistence through SQLAlchemy
- Pydantic request validation
- Pagination for doctor and patient lists
- Swagger UI and ReDoc documentation

## Project Structure

```text
.
├── main.py           # FastAPI application, models, authentication, and endpoints
├── admin.py          # Command-line script for creating an administrator
├── requirements.txt  # Python dependencies
└── README.md
```

## Requirements

- Python 3.10 or newer
- `pip`

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
pip install PyJWT pwdlib
```

`main.py` imports `PyJWT` and `pwdlib`; install them explicitly because they are not currently listed in `requirements.txt`.

## Configuration

Create a `.env` file in the project directory when custom configuration is needed:

```env
DATABASE_URL=sqlite:///./assignment2.db
SECRET_KEY=replace-this-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

The application uses the values above by default, except for `SECRET_KEY`, which should be changed before deployment.

## Run the Application

Start the development server from the project directory:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Database tables are created automatically when `main.py` starts. The default SQLite database is `assignment2.db`.

## Create an Administrator

Public registration creates doctor users only. Create an administrator with the command-line script:

```bash
python admin.py
```

The script asks for the administrator's name, email, and password.

## Authentication

Register or create a user, then log in:

```http
POST /auth/login
```

Example request:

```json
{
  "email": "doctor@example.com",
  "password": "secret123"
}
```

The response contains an access token:

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

Use the token in the `Authorization` header:

```text
Authorization: Bearer JWT_TOKEN
```

In Swagger UI, select **Authorize** and enter `Bearer JWT_TOKEN`.

## API Endpoints

### Authentication

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/` | Public | Health check |
| `POST` | `/auth/register` | Public | Register a doctor user |
| `POST` | `/auth/login` | Public | Log in and receive a JWT |

### Doctors

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/doctors` | Admin | Create a doctor |
| `GET` | `/doctors` | Authenticated | List active doctors |
| `GET` | `/doctors/{doctor_id}` | Authenticated | Get one active doctor |
| `PUT` | `/doctors/{doctor_id}` | Admin | Update a doctor |
| `DELETE` | `/doctors/{doctor_id}` | Admin | Soft-delete a doctor |

The doctor list accepts `skip`, `limit`, and `specialization` query parameters.

### Patients

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/patients` | Admin | Create a patient |
| `GET` | `/patients` | Doctor or Admin | List patients |
| `GET` | `/patients/{patient_id}` | Doctor or Admin | Get a patient |

The patient list accepts `skip` and `limit` query parameters. Doctors can see only their assigned patients.

### Doctor-Patient Assignments

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/doctors/{doctor_id}/patients/{patient_id}` | Admin | Assign a patient to a doctor |
| `GET` | `/doctors/{doctor_id}/patients` | Doctor or Admin | List a doctor's patients |

## Roles and Permissions

### Admin

- Create, update, list, and soft-delete doctors
- Create and view all patients
- Assign patients to doctors
- View any doctor's assigned patients

### Doctor

- View active doctors
- View their assigned patients
- View a patient only when assigned to them
- View their own assigned-patient list

Public registration cannot create an admin account.

## Validation Rules

- Names: 2-100 characters
- Passwords: 6-100 characters
- Patient age: greater than zero
- Patient phone: 10-15 digits
- List limits: 1-100 records per request

## Notes

- Deleting a doctor sets the doctor and linked user to inactive instead of removing database rows.
- Do not commit `.env` files, secret keys, or the generated SQLite database to version control.
# Doctor–Patient Management API

A production-ready backend application built using **FastAPI** for managing doctors, patients, authentication, authorization, and doctor–patient assignments.

---

## 📋 Project Overview

The **Doctor–Patient Management API** provides a secure backend system with:

- 🔐 JWT-based authentication
- 👥 Role-based authorization
- 👨‍⚕️ Admin and Doctor roles
- 🩺 Doctor management
- 🧑‍🤝‍🧑 Patient management
- 🔗 Doctor–patient assignment
- ✅ Input validation
- 💾 SQLite database persistence
- 🗑️ Soft deletion of doctors
- 📄 Swagger/OpenAPI documentation
- ⚙️ Environment-based configuration

The application follows a modular architecture with separate routers, models, schemas, services, and authentication modules.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Python 3.9+ | Programming language |
| FastAPI | Backend web framework |
| Pydantic | Request/response validation |
| SQLAlchemy | ORM/database interaction |
| SQLite | Database |
| JWT | Authentication |
| Uvicorn | ASGI server |
| Passlib/Bcrypt | Password hashing |
| python-dotenv | Environment configuration |
| Swagger/OpenAPI | API documentation |

---

## 📁 Project Structure

```text
doctor_patient_api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── doctors.py
│   │   └── patients.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── doctor_service.py
│       └── patient_service.py
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── doctor_patient.db
📦 Module Responsibilities
main.py
Creates the FastAPI application

Registers API routers

Initializes database tables

database.py
Configures the database

Creates the SQLAlchemy engine

Provides database session management

models.py
Contains SQLAlchemy database models:

User

Doctor

Patient

Doctor–Patient relationships

schemas.py
Contains Pydantic request and response models used for:

Input validation

Request serialization

Response validation

auth/
Handles:

Password hashing

JWT creation

JWT validation

Authentication

Role-based authorization

routers/
Contains API endpoints for:

Authentication

Doctors

Patients

services/
Contains the application's business logic and database CRUD operations.

🚀 Installation
1. Clone the Repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd doctor_patient_api

2. Create a Virtual Environment
Windows
python -m venv venv

Activate the environment:

venv\Scripts\activate

Linux / macOS
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

⚙️ Environment Configuration
Create a .env file in the project root:

DATABASE_URL=sqlite:///./doctor_patient.db
SECRET_KEY=change-this-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

Important: For production, use a strong randomly generated SECRET_KEY and do not commit your .env file to GitHub.

▶️ Run the Application
Start the FastAPI development server:

uvicorn app.main:app --reload

The application will run at:

http://127.0.0.1:8000

📚 API Documentation
FastAPI automatically provides interactive API documentation.

Swagger UI
http://127.0.0.1:8000/docs

ReDoc
http://127.0.0.1:8000/redoc

Swagger UI can be used to test all API endpoints directly from the browser.

👤 User Roles
The application supports two roles:

Admin

Doctor

👑 Admin
Admin users can:

Create doctors

View doctors

Update doctors

Soft-delete doctors

Create patients

View patients

Assign patients to doctors

👨‍⚕️ Doctor
Doctor users can:

Authenticate using JWT

View their assigned patients

Access only patients assigned to them

Doctors cannot:

Manage other doctors

Access another doctor's patients

🔐 Authentication APIs
Register
Endpoint
POST /auth/register

Admin Registration
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "Admin@123",
  "role": "admin"
}

Doctor Registration
{
  "username": "doctor1",
  "email": "doctor1@example.com",
  "password": "Doctor@123",
  "role": "doctor"
}

Login
Endpoint
POST /auth/login

Request
{
  "username": "admin",
  "password": "Admin@123"
}

Response
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}

Copy the access token and use it with the Authorize button in Swagger UI.

🩺 Doctor Management APIs
Create Doctor
POST /doctors

Authorization: Admin only

Request
{
  "name": "Dr. Ravi Kumar",
  "specialization": "Cardiology",
  "email": "ravi@example.com",
  "is_active": true
}

List Doctors
GET /doctors

Returns the list of doctors.

Get Doctor
GET /doctors/{doctor_id}

Example
GET /doctors/1

Update Doctor
PUT /doctors/{doctor_id}

Request
{
  "name": "Dr. Ravi Kumar",
  "specialization": "Neurology",
  "email": "ravi@example.com",
  "is_active": true
}

Delete Doctor
DELETE /doctors/{doctor_id}

The application uses soft deletion instead of permanently deleting the doctor.

The doctor is marked as:

{
  "is_active": false
}

🧑 Patient Management APIs
Create Patient
POST /patients

Request
{
  "name": "Prasanth",
  "age": 25,
  "phone": "9876543210"
}

List Patients
GET /patients

Returns the available patients.

Get Patient
GET /patients/{patient_id}

Example
GET /patients/1

🔗 Doctor–Patient Assignment
A doctor can have multiple patients.

Assign Patient to Doctor
POST /doctors/{doctor_id}/patients/{patient_id}

Example
POST /doctors/1/patients/1

This assigns patient 1 to doctor 1.

Get Doctor's Patients
GET /doctors/{doctor_id}/patients

Example
GET /doctors/1/patients

The response contains only the patients assigned to that doctor.

Doctors are restricted from viewing patients assigned to other doctors.

✅ Validation
The API implements request validation using Pydantic.

Email Validation
Email addresses must be valid and unique.

Valid
doctor@example.com

Invalid
doctor-example

Age Validation
Age must be greater than zero.

Valid
{
  "age": 25
}

Invalid
{
  "age": 0
}

Phone Validation
Phone numbers must contain between 10 and 15 digits.

Valid
9876543210

Invalid
12345

⚠️ Error Handling
The application uses FastAPI's HTTPException for API errors.

Common HTTP status codes include:

Status Code	Meaning
400	Bad Request
401	Unauthorized
403	Forbidden
404	Not Found
422	Validation Error

Example Error Response
{
  "detail": "Doctor not found"
}

💾 Database
SQLite is used as the database.

Database File
doctor_patient.db

Main Entities
Users

Doctors

Patients

Doctor_Patient

Relationship
Doctor
   │
   ├── Patient
   ├── Patient
   └── Patient

A many-to-many relationship is used so the database can support multiple patient assignments.

🧪 Testing
The APIs can be tested using:

FastAPI Swagger UI

Postman

cURL

Swagger UI
http://127.0.0.1:8000/docs

Recommended Testing Sequence
Register Admin

Login Admin

Authorize JWT

Create Doctor

Create Patient

Assign Patient

Get Doctor's Patients

Register Doctor

Login Doctor

Verify Doctor can access assigned patients

Verify Doctor cannot access another doctor's patients

Verify Admin-only endpoints return 403 for Doctor

Test invalid email

Test invalid age

Test invalid phone

Test duplicate email

Test non-existing Doctor/Patient

📋 Requirements
Install all dependencies using:

pip install -r requirements.txt

To generate or update requirements.txt:

pip freeze > requirements.txt