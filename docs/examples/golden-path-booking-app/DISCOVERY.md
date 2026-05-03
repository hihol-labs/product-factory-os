# DISCOVERY

## Problem

Private tutors manage availability and bookings manually across chat messages and spreadsheets.

## Target Users

- Independent tutors with recurring availability
- Students or parents booking a lesson slot

## Current Alternatives

- Chat scheduling
- Google Calendar links
- Generic booking tools

## Positioning

A narrow booking MVP for tutors: publish slots, book slots, and track upcoming lessons without payment complexity.

## MVP Scope

- Tutor account
- Student account
- Availability slots
- Booking creation and cancellation
- Local admin visibility through database or simple dashboard

## Feature Priorities

| Feature | MoSCoW | RICE | Reason |
|---|---|---:|---|
| Auth | Must | 80 | Required for ownership |
| Availability slots | Must | 90 | Core supply-side flow |
| Booking flow | Must | 95 | Core demand-side flow |
| Payments | Won't | 20 | Deferred to reduce scope |
| Calendar sync | Won't | 25 | Useful later, not MVP-critical |

## Assumptions

- Local MVP is acceptable before hosted deployment.
- SQLite is enough for first validation.
- Payments are not needed for first release.

## Risks

- Double-booking if slot locking is weak.
- Time zone handling can become complex.

