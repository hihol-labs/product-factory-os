# Notes

This fixture checks that production deploys require confirmation, production readiness preflight, verification, rollback notes, and session memory.

## Scenario 1: Explicit Confirmation

The deploy route asks for the target environment and impact confirmation before any real command.

## Scenario 2: Failed Verification

If health checks or smoke checks fail, the report includes rollback steps and does not claim success.

## Scenario 3: State Save

Every production deploy attempt records session context and verification evidence.
