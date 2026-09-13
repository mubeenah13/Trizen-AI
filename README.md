# TrizenAI Photo Sharing Platform — Full-Stack Internship Challenge

A collaborative, production-ready full-stack event photography platform built for event teams, lead photographers, and customer galleries. Built for the **TrizenAI Full-Stack Internship Challenge**.

---

## 🌟 Features Overview

- 👑 **Lead Admin Management**: Create events, assign team members, review uploaded event photos, bulk select photos, set gallery PINs, and publish customer galleries.
- 📸 **Photographer Team Portal**: View assigned events, upload multiple high-resolution photos with drag-and-drop, and view uploaded event photographs.
- 🔒 **Server-Side RBAC**: Role-based access control enforcing Admin vs Team Member permissions across every API route.
- 🔑 **PIN-Protected Customer Gallery**: Customers access published galleries via shareable URLs (`/gallery/:slug`) and 4-8 digit numeric PINs without creating an account.
- 🛡️ **Bcrypt PIN Hashing & Scoped JWT**: PINs are hashed using bcrypt. Customer verification returns a short-lived, gallery-scoped JWT token.
- 🛡️ **Unpublished Photo Security**: Customer APIs return ONLY photos explicitly added to published galleries. Unpublished photos are strictly inaccessible.
- 📦 **S3 Object Storage Integration**: Image files are uploaded to S3/MinIO object storage; PostgreSQL stores metadata only. Includes proxy streaming and failure rollback / orphan object cleanup.
- 🐳 **Docker & Docker Compose**: Single command containerized deployment (`docker compose up --build`).

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, React Router v6, TanStack Query, Axios, Lucide React |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic, PyJWT, Passlib (bcrypt) |
| **Database** | PostgreSQL 16 (production) / SQLite async (local fallback) |
| **Object Storage** | S3-compatible Object Storage (MinIO / AWS S3) |
| **Infrastructure** | Docker, Docker Compose, Nginx |
| **Testing** | pytest, pytest-asyncio, httpx |

---

## 🔐 Security & RBAC Matrix

| Endpoint / Action | Admin | Team Member | Customer (Public) |
| :--- | :---: | :---: | :---: |
| Register / Login | ✅ | ✅ | ❌ |
| Create Event | ✅ | ❌ (403) | ❌ |
| View Assigned Events | ✅ (All) | ✅ (Assigned) | ❌ |
| Upload Photos | ✅ | ✅ (Assigned) | ❌ |
| Delete Photo | ✅ | ✅ (Own Upload) | ❌ |
| Create / Publish Gallery | ✅ | ❌ (403) | ❌ |
| Verify Gallery PIN | N/A | N/A | ✅ (Public) |
| View Published Photos | ✅ | ✅ | ✅ (With PIN Token) |
| View Unpublished Photos | ✅ | ✅ (Assigned) | ❌ (403/404) |

---

## 🔑 Demo Credentials & Test Scenarios

### Pre-Seeded Accounts (Auto-Created on Startup)

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Lead Admin** | `admin@trizen.ai` | `Admin123!` | Full Admin Dashboard, Event & Gallery Creation |
| **Team Member** | `team@trizen.ai` | `Team123!` | Assigned to "TrizenAI Annual Tech Gala 2026" |

### Pre-Seeded Demo Customer Gallery

- **Demo Gallery URL**: `http://localhost:5173/gallery/gala-highlights-2026`
- **Demo Gallery PIN**: `123456`

---

## 🚀 Quick Setup Guide

### Option 1: Running via Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/trizen-ai/photo-sharing-platform.git
cd photo-sharing-platform

# 2. Copy environment file
cp .env.example .env

# 3. Launch full stack (Postgres, MinIO, Backend, Frontend)
docker compose up --build
```

Access services:
- **Frontend App**: `http://localhost:5173`
- **FastAPI Backend Docs**: `http://localhost:8000/api/v1/docs`
- **MinIO Console**: `http://localhost:9001` (User: `minioadmin`, Pass: `minioadmin`)

---

### Option 2: Running Locally (Standalone Development)

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment & install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database seeder (Creates SQLite DB & demo data)
python -m app.seed

# Start FastAPI dev server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

---

## 🧪 Running Automated Test Suite

```bash
cd backend

# Run full pytest suite (18 automated tests covering Auth, RBAC, Uploads, PIN, Public Gallery security)
python -m pytest tests/ -v
```

## 🛡️ Storage & Database Failure Behavior

- **Object Storage**: Local storage is available as a development fallback. Production uses durable S3-compatible object storage (AWS S3 / Cloudflare R2). If S3 becomes unavailable in production, the backend fails gracefully (`HTTP 503 Service Unavailable`) rather than treating local ephemeral disk as durable storage.
- **Database Availability**: Production deployment should use managed PostgreSQL with automated backups and multi-AZ failover.

| Scenario | Requirement | Status | Verification Method |
| :---: | :--- | :---: | :--- |
| 1 | Admin creates event | ✅ | Verified via Admin Dashboard |
| 2 | Admin adds Team Member | ✅ | Verified via Event Details |
| 3 | Team Member assigned event view | ✅ | Verified via Team Dashboard |
| 4 | Team Member multi-photo upload | ✅ | Verified via Drag & Drop Uploader |
| 5 | Admin photo review & uploader info | ✅ | Verified via Photo Grid |
| 6 | Admin photo bulk selection | ✅ | Verified via Selection Bar |
| 7 | Team Member publish attempt blocked | ✅ | Tested via Pytest (`403 Forbidden`) |
| 8 | Admin publishes gallery with PIN | ✅ | Verified via Create Gallery Modal |
| 9 | Customer opens shareable URL | ✅ | Verified via `/gallery/:slug` |
| 10 | Customer enters incorrect PIN | ✅ | Tested via Pytest (`401 Unauthorized`) |
| 11 | Customer enters correct PIN | ✅ | Verified token issue & gallery unlock |
| 12 | Customer access to unpublished photo | ✅ | Tested via Pytest (`403 Access Denied`) |
| 13 | Unauthorized event access blocked | ✅ | Tested via Pytest (`403 Access Denied`) |
| 14 | Photo upload failure rollback | ✅ | Verified orphan cleanup in StorageService |

---

## 📜 Architecture Documentation

For deep-dive architectural decisions, database ER diagrams, security threat models, and interview questions, see [`architecture/architecture.md`](file:///c:/Trizen%20AI/architecture/architecture.md).
