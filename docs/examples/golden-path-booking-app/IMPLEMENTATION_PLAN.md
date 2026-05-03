# IMPLEMENTATION_PLAN

## Steps

| Step | Goal | Files | Verification | Exit Criteria |
|---:|---|---|---|---|
| 1 | Scaffold FastAPI app | `pyproject.toml`, `app/main.py`, `tests/` | `pytest` | App imports and health test passes |
| 2 | Add models and DB setup | `app/db.py`, `app/models.py` | `pytest tests/test_models.py` | Tables can be created |
| 3 | Add auth | `app/auth.py`, `app/routes/auth.py` | `pytest tests/test_auth.py` | Register/login works |
| 4 | Add slots | `app/routes/slots.py` | `pytest tests/test_slots.py` | Tutor can create slot |
| 5 | Add bookings | `app/routes/bookings.py` | `pytest tests/test_bookings.py` | Student books slot and double-booking fails |
| 6 | Add README and Docker | `README.md`, `Dockerfile` | `docker build .` or documented skip | Local run documented |

## Deferred Work

- Payments
- Calendar sync
- Hosted production deploy

## Release Gate

- Tests pass.
- `/review` is not `BLOCKED`.
- `/security-audit` has no Critical findings.

