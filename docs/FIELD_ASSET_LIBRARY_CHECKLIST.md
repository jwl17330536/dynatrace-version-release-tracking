# Field Asset Library Submission Checklist

## Folder and Naming
- [ ] Asset path uses `/{asset-type}/{use-case}/{asset-name}/`.
- [ ] `asset-type` is approved.
- [ ] `use-case` is approved and matches `meta.yaml` exactly.
- [ ] `asset-name` is lowercase and hyphen-separated.

## Required Files (Dashboard)
- [ ] `meta.yaml`
- [ ] `README.md`
- [ ] `screenshot.png`
- [ ] One or more meaningful `*.json` dashboard files

## Metadata Quality
- [ ] `title` and `description` are complete.
- [ ] `purpose` is plain-language, problem + benefit, and >= 50 chars.
- [ ] `author` and `contact` are set.
- [ ] `asset_type` and `use_case` are correct.
- [ ] `deployment` includes SaaS, Managed, or both.
- [ ] At least one approved tag is set.
- [ ] `setup_instructions` are actionable.
- [ ] `tenant_url` is set when required by policy.

## Security and Data Hygiene
- [ ] No tokens, credentials, or customer-confidential data.
- [ ] No private environment links outside permitted `tenant_url` usage.

## Validation
- [ ] Asset tested in a real Dynatrace environment.
- [ ] Dashboard shared with Use Case Playground User group.
- [ ] JSON files parse and import cleanly.

## PR Workflow
- [ ] Branch name follows `{asset-type}/{initials}-{short-description}`.
- [ ] PR checklist completed.
- [ ] CI passes before requesting review.
- [ ] SE Enablement review requested.
