# Packaging

Install or refresh the local Product Factory OS checkout:

```bash
bash packaging/install.sh --workspace /home/hihol/projects --install-hooks
```

The installer validates runtime contracts, routing fixtures, and hook metadata. With `--install-hooks`, it copies hook scripts into `${CODEX_HOME:-$HOME/.codex}/hooks/product-factory-os/` but does not silently mutate global Codex settings.

Run release checks:

```bash
python3 scripts/release_check.py
```
