## Summary

<!-- 1–3 sentences: why this change exists (phase gate, bug, risk). -->

## Type

- [ ] `feat` — new capability
- [ ] `fix` — bug fix
- [ ] `docs` — docs / governance / evidence only
- [ ] `ci` — CI / pre-commit / Actions
- [ ] `chore` — tooling, lockfile, scaffolding
- [ ] `security` — authn/authz, secrets, supply chain
- [ ] `refactor` — no intentional behavior change
- [ ] `test` — tests only

## Phase / guide impact

- Phase card(s): <!-- e.g. phase-02-data-contract.md -->
- [ ] Stays within the phase card **Allowed paths**
- [ ] No guide-baseline behavior change **or** GUIDE_TRACEABILITY rows updated
- [ ] Model/data/split impacting change called out for model + data owner review
- [ ] `docs/implementation/STATUS.md` updated if a phase exits

## Test plan

- [ ] `pre-commit run --all-files`
- [ ] `pytest -q` (note any intentional skips)
- [ ] No full CIFAR-10 training in PR CI
- [ ] Extra verification: <!-- commands / screenshots / evidence paths -->

## Security

- [ ] No secrets, keys, `.env`, or tfstate committed
- [ ] No long-lived cloud keys added to Actions
- [ ] Dependency/Action pins are immutable where required
- [ ] N/A or risk ID if audit findings are accepted: <!-- e.g. CYB-07 -->

## Risk / rollback

<!-- What breaks if this is wrong? How do we revert? -->

## Checklist

- [ ] Title follows `type(scope): summary`
- [ ] PR is focused (or stacked PRs linked)
- [ ] Conversations will be resolved before merge
- [ ] CODEOWNERS paths reviewed when touched
