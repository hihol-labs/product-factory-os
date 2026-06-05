# Fallback Policy

## Allowed Fallbacks

- Retry.
- Queue for later processing.
- Explicit degraded/unavailable status.
- Cached data with freshness metadata.
- Test/dev fixtures outside production paths.

## Forbidden Fallbacks

- Fake production results.
- Invented provider responses.
- Synthetic real-world data presented as real.
- Silent substitution without user/developer-visible status.

## Project-Specific Fallbacks

- If `/usr/local/bin/pfo` cannot be updated because of permissions, keep the managed `~/.local/bin/pfo` wrapper and emit a visible warning naming the skipped target.
- If a contract gate sees only generated PFO runtime/status artifacts, record them under `runtimeChangedFiles` and avoid product security evidence blockers.
- If external connectors or credentials are unavailable, continue with local validators and record the unavailable evidence explicitly.
- If repository analysis cannot infer stack commands, keep adoption artifacts current and report the analyzer limitation without inventing commands.
