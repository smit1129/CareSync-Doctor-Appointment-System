# CareSync — Doctor Appointment Management System

CareSync is a professional, full-stack healthcare appointment management platform built as a complete solution for patients, doctors, and administrators. It features role-based access control, concurrency-safe double-booking prevention, automated notifications, payment processing (simulated), and a modern, fully responsive UI.

## Features

### 👤 Patients
- **Search & Filter:** Find doctors by name, specialization, or clinic location.
- **Book Appointments:** Pick an available time slot and book securely.
- **Manage History:** View upcoming and past appointments, and cancel if needed.
- **Feedback & Rating:** Rate doctors and share experiences post-consultation.

### 👨‍⚕️ Doctors
- **Profile Management:** Update specialization, clinic address, bio, and consultation fees.
- **Schedule Availability:** Define custom working hours and slot durations (e.g., 15/30/60 minutes).
- **Appointment Actions:** Accept, reject, or mark appointments as completed.

### ⚙️ Admins
- **System Dashboard:** View high-level metrics (total doctors, patients, revenue, and appointment statuses).
- **User Management:** Add new doctors to the platform and view patient registries.
- **Reporting:** Robust endpoints for monthly appointment and revenue reports.

## Technology Stack

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database:** SQLite (with WAL mode for concurrent writes) & SQLAlchemy ORM
- **Authentication:** JWT (JSON Web Tokens) with Role-Based Access Control (RBAC)
- **Validation:** Pydantic models

### Frontend
- **Framework:** [Next.js](https://nextjs.org/) (React, App Router)
- **Styling:** Tailwind CSS (Modern, premium aesthetic with gradients, blurs, and glassmorphism)
- **State Management:** React Context API & Hooks

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Backend Setup

```bash
# Navigate to the project root
cd "Doctor Appointment Management System"

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run database setup & seeding
python backend/seed_data.py

# Start the FastAPI server
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be running at `http://localhost:8000`.
API Documentation (Swagger UI) is available at `http://localhost:8000/docs`.

### Security / Environment Setup

Before running in production, ensure the following:
- Copy `.env.example` to `.env` and configure your environment variables.
- Set a strong `SECRET_KEY` in your `.env` file (e.g. `openssl rand -hex 32`).
- Never commit the `.env` file or any real secrets to version control.
- Set `FRONTEND_URL` in your backend `.env` to restrict CORS to your production domain.
- The password reset flow currently logs the token in local dev instead of emailing it, configure an email provider for real production usage.
- Payments are in demo/test mode and use simulated processing.

### 2. Frontend Setup

```bash
# Navigate to the frontend directory
cd "Doctor Appointment Management System"/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be running at `http://localhost:3000`.

## Demo Credentials (LOCAL/DEVELOPMENT ONLY)

You can use the following pre-seeded accounts to explore the system locally. Do NOT use these in a production environment:

| Role | Email | Password |
|---|---|---|
| **Patient** | `john.doe@gmail.com` | `Patient@12345` |
| **Doctor** | `sarah.jenkins@hospital.com` | `Doctor@12345` |
| **Admin** | `admin@hospital.com` | `Admin@12345` |

## Core Highlights

1. **Concurrency Safety:** Enforces unique active slots at the database level (`idx_unique_active_doctor_slot`) using SQLite partial indexes. This ensures multiple patients cannot double-book a doctor at the exact same time.
2. **Dynamic Slot Generation:** The backend computes available slots on the fly based on the doctor's defined schedule and filters out any already-confirmed appointments.
3. **Comprehensive Test Suite:** Includes 23 passing Lab Manual test cases (including security tests for RBAC and SQL injection prevention), verifying the entire business logic flow.
