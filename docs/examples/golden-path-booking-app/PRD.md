# PRD

## Goals

- Let tutors publish available lesson slots.
- Let students book an available slot.
- Prevent double-booking.

## Non-Goals

- Payments
- Calendar sync
- Multi-language UI
- Production deployment

## Personas

- Tutor: wants to publish available time without manual coordination.
- Student: wants to reserve a lesson quickly.

## User Stories

### P0

- As a tutor, I can create available slots.
- As a student, I can view available slots.
- As a student, I can book one available slot.
- As a tutor, I can see upcoming bookings.

### P1

- As a student, I can cancel a booking.
- As a tutor, I can remove an available slot.

### P2

- Email reminders.
- Calendar export.

## Acceptance Criteria

- A slot cannot be booked twice.
- Booked slots no longer appear as available.
- Tutor can distinguish open slots from booked slots.

## Launch Criteria

- Local run instructions work.
- Booking flow has automated tests.
- Review status is not `BLOCKED`.

## Kill Criteria

- Users require payment support before using the MVP.
- Time zone requirements exceed local MVP assumptions.

