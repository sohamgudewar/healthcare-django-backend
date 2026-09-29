# Healthcare Backend API

Backend system for a healthcare application built with **Django**, **Django REST Framework (DRF)**, **SimpleJWT**, and **PostgreSQL**.

---

## Quick Start

### Option 1: Docker (Recommended)
```bash
docker compose up --build
```
*Starts PostgreSQL, applies migrations, seeds sample data, and runs the server at `http://localhost:8000`.*

### Option 2: Local Setup
```bash
# 1. Virtual Environment
python -m venv venv
.\venv\Scripts\activate       # On Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# 2. Configure Environment
cp .env.example .env

# 3. Migrate, Seed Data & Run
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

---

## Test Credentials

Created automatically when running `seed_data`:

| Role | Email | Password |
| :--- | :--- | :--- |
| **Clinician User** | `doctor.demo@healthcare.com` | `DoctorPass123!` |
| **Admin User** | `admin@healthcare.com` | `AdminPass123!` |

---

## API Endpoints

### 1. Authentication
| Method | Endpoint | Auth | Description |
| :---: | :--- | :---: | :--- |
| `POST` | `/api/auth/register/` | None | Register new user with `name`, `email`, `password` |
| `POST` | `/api/auth/login/` | None | Log in and receive JWT `access` and `refresh` tokens |
| `POST` | `/api/auth/token/refresh/` | None | Refresh access token |
| `GET` | `/api/auth/me/` | Bearer | Get authenticated user profile |

### 2. Patient Management
| Method | Endpoint | Auth | Description |
| :---: | :--- | :---: | :--- |
| `POST` | `/api/patients/` | Bearer | Add a new patient |
| `GET` | `/api/patients/` | Bearer | Retrieve all patients created by the authenticated user |
| `GET` | `/api/patients/<id>/` | Bearer | Get details of a specific patient |
| `PUT` | `/api/patients/<id>/` | Bearer | Update patient details |
| `DELETE`| `/api/patients/<id>/` | Bearer | Delete a patient record |

### 3. Doctor Management
| Method | Endpoint | Auth | Description |
| :---: | :--- | :---: | :--- |
| `POST` | `/api/doctors/` | Bearer | Add a new doctor (unique license & email checked) |
| `GET` | `/api/doctors/` | Bearer | Retrieve all doctors (supports `?search=` and `?specialization=`) |
| `GET` | `/api/doctors/<id>/` | Bearer | Get details of a specific doctor |
| `PUT` | `/api/doctors/<id>/` | Bearer | Update doctor details |
| `DELETE`| `/api/doctors/<id>/` | Bearer | Delete a doctor record |

### 4. Patient-Doctor Mapping
| Method | Endpoint | Auth | Description |
| :---: | :--- | :---: | :--- |
| `POST` | `/api/mappings/` | Bearer | Assign a doctor to a patient (prevents duplicates) |
| `GET` | `/api/mappings/` | Bearer | Retrieve all patient-doctor mappings |
| `GET` | `/api/mappings/<patient_id>/` | Bearer | Get all doctors assigned to a specific patient |
| `DELETE`| `/api/mappings/<id>/` | Bearer | Remove a doctor from a patient |

---

## Interactive Documentation & Testing

- **Swagger UI:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc:** [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **Postman Collection:** Import `healthcare_api_postman_collection.json` (auto-extracts JWT token on login).

---

## Running Tests

Run the 35 automated tests:

```bash
pytest
```
*or*
```bash
python manage.py test tests
```
```text
35 passed in ~20s (100% pass rate)
```
