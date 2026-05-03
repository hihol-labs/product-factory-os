# Product Blueprint

## Product Classification

```text
PRODUCT_TYPE: SaaS Application
DOMAIN: tutor booking
COMPLEXITY: medium
REQUIRED_MODULES: auth, database, api, dashboard, booking, notifications
INFRASTRUCTURE: local Docker, SQLite for MVP, PostgreSQL-ready schema
```

## Business Logic

Tutors publish available time slots. Students search tutors and book slots. The MVP defers payments and calendar sync.

## Users And Roles

- Tutor: manages profile and availability.
- Student: searches and books slots.
- Admin: optional future role for moderation.

## Core Entities

| Entity | Purpose | Fields | Relationships |
|---|---|---|---|
| User | Authenticated account | id, email, passwordHash, role, createdAt | owns TutorProfile or StudentProfile |
| TutorProfile | Tutor public profile | id, userId, name, subject, bio, hourlyRate | has many AvailabilitySlot |
| AvailabilitySlot | Bookable tutor time | id, tutorId, startsAt, endsAt, status | may have one Booking |
| Booking | Student reservation | id, slotId, studentId, status, createdAt | belongs to slot and student |

## Modules

| Module | Responsibility | Depends On | Template Contract |
|---|---|---|---|
| auth | Signup, login, sessions, roles | database | auth |
| tutor-profile | Tutor profile CRUD | auth, database | dashboard, api |
| availability | Slot creation and status changes | auth, database | services, db_layer |
| booking | Booking flow and conflict checks | auth, availability | services, api |
| dashboard | Tutor/student UI | auth, api | dashboard |

## Interfaces

- Pages: login, dashboard, tutor profile, availability, booking.
- API: auth, profiles, slots, bookings.
- Commands: local dev, test, migration.

## Infrastructure

- Runtime: Node or Python web stack selected during implementation.
- Database: SQLite for local MVP, PostgreSQL-compatible schema.
- Deployment target: local Docker first.

## Risks And Assumptions

- Payments and external calendar sync are deferred.
- Booking conflicts must be prevented transactionally.

