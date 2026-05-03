# Integrations

Product Factory OS exports project state into integration payloads for:

- GitHub Issues
- Linear
- Notion

Generate payloads:

```bash
python3 scripts/export_integrations.py ../my-product --target github
python3 scripts/export_integrations.py ../my-product --target linear
python3 scripts/export_integrations.py ../my-product --target notion
```

The payloads are written to `.pfo-integrations/`.

