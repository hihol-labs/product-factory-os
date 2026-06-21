# Acceptance Contract Gate

The acceptance contract is the runtime link between the original user request and final verification.

Before implementation, PFO must create `.pfo/ACCEPTANCE_CONTRACT.json` with:

- the original request;
- one or more explicit acceptance criteria;
- a source quote for each criterion;
- the verification method that will prove each criterion.

After implementation, every criterion must be `PASSED` with evidence before `pfo verify-work --pass-gate` can pass. Evidence that relies on a validator changed in the same unit must include independent evidence, such as a separate command, review, or artifact.

Commands:

```bash
pfo acceptance init <project> --request "..." --criterion "AC1::requirement::verification"
pfo acceptance verify <project> --id AC1 --status PASSED --evidence-kind command --evidence "..."
pfo acceptance gate <project>
```

This is a feedback sensor paired with the feedforward unit manifest and verification contract. It fails closed when criteria are missing, pending, failed, waived without approval, or proved only by weak self-authored validation.
