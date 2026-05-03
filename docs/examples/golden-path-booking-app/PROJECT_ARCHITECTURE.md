# PROJECT_ARCHITECTURE

## Stack

- Backend: FastAPI
- Database: SQLite for MVP
- Tests: pytest
- Packaging: Docker-ready Python app

## Rationale

FastAPI and SQLite keep the MVP small while preserving a path to PostgreSQL.

## Data Model

### users

- id: integer primary key
- email: text unique
- password_hash: text
- role: text, `tutor` or `student`
- created_at: datetime

### slots

- id: integer primary key
- tutor_id: foreign key to users.id
- starts_at: datetime
- ends_at: datetime
- status: text, `open` or `booked`

Indexes:

- slots(tutor_id, starts_at)
- slots(status, starts_at)

### bookings

- id: integer primary key
- slot_id: foreign key to slots.id unique
- student_id: foreign key to users.id
- created_at: datetime
- status: text, `active` or `cancelled`

Indexes:

- bookings(student_id, created_at)

## API

- `POST /auth/register`
- `POST /auth/login`
- `POST /slots`
- `GET /slots`
- `POST /bookings`
- `GET /bookings`
- `POST /bookings/{id}/cancel`
- `GET /health`

## Auth And Permissions

- Tutors can create and delete their own slots.
- Students can create and cancel their own bookings.
- Auth is token-based for MVP.

## Deployment Topology

Local app plus SQLite file. Docker can package the API when deploy target is selected.

## Observability

- `/health` endpoint
- Structured request logs

## Risks And Tradeoffs

- SQLite is simple but not ideal for concurrent production writes.
- Time zones need stricter handling before production.

