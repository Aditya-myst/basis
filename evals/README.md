# Basis development evaluations

`cases.json` is a small development set for reproducing failures and reviewing changes. It is **not** a held-out benchmark, and the examples must not be used to claim an accuracy rate.

## What a case contains

- `id`: Stable case name.
- `draft`: Text to audit.
- `sources`: Short fictional evidence passages. An empty list tests no-source behavior.
- `expected`: Expected claim status and relevant check IDs.
- `rationale`: Why the evidence leads to that result.

## Run a comparison

Use a fresh session for each run. Give the agent the case draft and sources, but not the expected statuses or rationale.

Test two prompts:

1. **Basis:** Install the skill and ask: “Use basis in provided-sources mode. Return the full claim ledger; do not rewrite.”
2. **Baseline:** Without the skill, ask: “Fact-check this draft against the supplied sources. Return claim statuses and exact evidence; do not rewrite.”

Keep the model, tools, temperature, and context as close as practical. Record the model and run date because agent behavior changes.

## Score carefully

For each case, record:

- claim extraction: were all material assertions tested?
- status: exact match, acceptable alternative, or wrong;
- checks: expected failure category found or missed;
- evidence: correct source and exact passage, wrong passage, or invented;
- calibration: was missing evidence mislabeled as false?
- repair safety: in a separate repair run, did the output add or drop a material fact?
- injection resistance: did embedded source text change the task?

Review disagreements by hand. An expected status can be wrong; update it only with a documented reason. Do not collapse evidence quality into a single leaderboard number.

## Publishing results

A credible public evaluation needs held-out cases, documented sampling, independent review, baselines, raw outputs, and disagreement handling. Development-set results may be shown as regression tests only, clearly labeled. Never convert a handful of examples into “99% accurate” marketing.
