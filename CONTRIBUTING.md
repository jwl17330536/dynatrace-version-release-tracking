# Contributing

This repo serves two audiences. Pick the section that matches what you're doing.

---

## For Operators — running and maintaining the workflow

If you just want to install, run, and keep the workflow healthy — you don't need to change any code.

- **Install**: [QUICK_START.md](QUICK_START.md)
- **Day-2 operations** (token rotation, schedule management, troubleshooting): [docs/OPERATING.md](docs/OPERATING.md)
- **Deploy updates to your tenant without touching the Dynatrace UI**: [docs/DEPLOYING.md](docs/DEPLOYING.md)

---

## For Developers — modifying or extending the workflow

### Versioning rules (non-negotiable)

1. Always version workflow and dashboard together as a pair.
2. Workflow `vN` must update only dashboard `vN`.
3. Never edit a prior version in place for behavior changes.
4. Every behavior change creates a new `vN+1` workflow + dashboard pair.
5. After enabling `vN+1`, disable the `vN` schedule.
6. Keep exactly one active Version Intelligence workflow schedule at all times.

### Iteration cycle

1. Clone the repo and set up your personal config file:
   ```
   cp local-only/my-config.example.json local-only/my-config.json
   # Edit local-only/my-config.json with your real vault IDs and dashboard UUID
   ```
2. Edit the workflow or dashboard JSON in `workflows/` and `dashboards/`
3. Test your changes:
   ```bash
   make deploy-dry          # preview merged output without deploying
   make deploy              # deploy to your Dynatrace tenant via dtctl
   ```
4. Run validation:
   ```bash
   make static
   python3 scripts/run_validation_suite.py --profile canonical
   ```
5. When ready to publish a new version, create a `vN+1` pair and open a PR

### Workflow guide

Every workflow version must include an operator guide pasted into Dynatrace's Workflow Guide panel. The source markdown lives in `docs/WORKFLOW_GUIDE_V10.md`. After deploying via dtctl, re-paste the guide manually in Workflow options because dtctl does not round-trip the guide field.

### Validation commands

```bash
make help             # list all make targets
make self-check       # repo hygiene check
make static           # static validation of canonical assets
make ci-check         # full CI check suite
make deploy-dry       # preview deployment without pushing to Dynatrace
make deploy           # deploy to Dynatrace tenant
```

For legacy compatibility checks (only when touching v4/v5 assets):
```bash
python3 scripts/run_validation_suite.py --profile v5
```

### Security rules

- Never commit secrets, tokens, or tenant-specific IDs.
- Use `<PLACEHOLDER>` format in committed JSON artifacts.
- Keep personal config in `local-only/my-config.json` (gitignored).
- Run `make self-check` before opening a PR to catch any accidental leaks.
