## What changed?

<!-- Lead with the user-visible behavior. -->

## Why?

<!-- Link the issue or include a minimal evidence example. -->

## Checks

- [ ] `python3 scripts/validate-package.py`
- [ ] `python3 scripts/validate-report.py examples/report.json`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Skill discovery tested with the Skills CLI when package files changed
- [ ] README check tables, schema bounds, examples, and evals updated when checks changed
- [ ] Package versions and `CHANGELOG.md` updated for a release or behavior change
- [ ] No private data, invented sources, or unsupported performance claims added

## Evaluation

<!-- List the cases run and any wrong or uncertain results. Do not report development cases as a held-out benchmark. -->
