# Contributing

## Versioning Rules

1. Always version workflow and dashboard together.
2. Never edit prior versions in place for behavior changes.
3. Create `vN+1` artifacts for each behavior iteration.

## Local Scaffolding Workflow

Keep personal and machine-specific files local-only:

1. `.env.local` or `.env.*.local` for local values.
2. `local-only/` for private notes and runbooks.
3. `*.local.md` for local documentation.

Tracked files that must become local-only should be untracked before relying on `.gitignore`.

## Validation

```bash
make self-check
python3 scripts/run_validation_suite.py --profile canonical
make static
bash scripts/run_ci_smoke.sh static
```

Run legacy compatibility checks only when changing v4/v5 compatibility assets:

```bash
python3 scripts/run_validation_suite.py --profile v5
```

## Documentation

Keep `README.md` and `QUICK_START.md` synchronized with setup and runtime behavior.
