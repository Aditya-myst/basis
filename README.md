# Basis

> **Every claim needs a basis.**  
> Evidence lint for AI-written text.

Basis is a portable agent skill that checks factual writing against sources the agent actually read. It finds unsupported claims, broken claim-to-citation links, misleading quotations, numerical errors, stale evidence, and causal overreach. It can then repair the draft without filling gaps with new inventions.

It works with agents that support Markdown skills, including Claude Code, Codex, Cursor, and other agents supported by the Skills CLI.

**The difference is the evidence trail.** Basis does not stop at “this may be inaccurate.” It identifies the exact claim, assigns a precise status, quotes the relevant evidence, explains the problem, and limits the repair to what that evidence supports.

## Before and after

This example is fictional. The sources are supplied with the draft.

**Draft**

> In a 2024 lab test, the Aero One lasted 22 hours, so it delivers all-day battery life in every situation. A reviewer called it “the best battery we've tested.” Sales doubled after launch, proving the battery drove growth.

**Checked evidence**

- **S1, lab report:** A prototype played video for 22 hours at 150 nits in November 2024.
- **S2, review:** The reviewer wrote “among the longest-lasting batteries we've tested this year.”
- **S3, quarterly report:** Unit sales rose from 10,000 to 20,000 after launch; the same report records a concurrent marketing campaign.

**Basis findings**

| Claim | Status | Problem |
| --- | --- | --- |
| All-day battery life in every situation | `unsupported` | One video-playback test does not cover every use or condition. |
| “The best battery we've tested” | `contradicted` | The checked quotation says “among the longest-lasting” and limits the comparison to that year. |
| Sales doubled after launch | `supported` | The source reports 10,000 to 20,000 units in the relevant periods. |
| The battery drove growth | `unsupported` | Timing alone does not establish causation; another campaign ran at the same time. |

**Repaired text**

> In a November 2024 lab test, an Aero One prototype played video for 22 hours at 150 nits. A reviewer placed it among the longest-lasting batteries they had tested that year. Unit sales rose from 10,000 to 20,000 after launch; the checked evidence does not establish what caused the increase.

No made-up replacement fact. No fake confidence score. No claim that an inaccessible source was checked.

## Why Basis?

Generic fact-check prompts often fail in predictable ways:

- They treat a real-looking citation as proof without reading it.
- They call a claim false when they merely failed to find support.
- They “fix” one hallucination by adding another.
- They count repeated reporting as independent confirmation.
- They return an accuracy percentage with no defensible method.
- They hide research limits behind a clean rewrite.

Basis makes those failures explicit. It separates **source access**, **evidence**, **verdict**, and **repair**, then audits the result a second time.

## Installation

Replace `Aditya-myst` with the GitHub account or organization that hosts your copy.

### Claude Code

```text
/plugin marketplace add Aditya-myst/basis
/plugin install basis@basis
```

The plugin responds to `/basis:basis`. Use a current version of Claude Code. If plugin installation is unavailable, use the Skills CLI command below with `--agent claude-code`.

### Codex

```bash
npx skills add Aditya-myst/basis --global --agent codex
```

### Claude.ai and Claude Desktop

Download the repository as a ZIP and upload it as a skill in Settings. Keep `SKILL.md` at the ZIP root.

### Other agents

```bash
npx skills add Aditya-myst/basis --global --agent '*'
```

This installs Basis for agents supported by the Skills CLI. Leave off `--global` to install it only in the current project. For another agent, copy `SKILL.md` into its skill folder.

### Try a local checkout

```bash
git clone https://github.com/Aditya-myst/basis.git
cd basis
npx skills add . --global --agent '*'
```

## Usage

Call the skill directly or ask for it in plain language.

### Audit and repair with supplied sources

```text
/basis

Draft:
[paste the text]

Sources:
[paste sources, file paths, or URLs]
```

The default response contains an audit, findings, revised text, checked sources, and coverage limits.

### Audit without rewriting

```text
Use basis to audit this draft. Do not rewrite it. Check every material claim
against the two attached reports and return the full claim ledger.

[paste draft]
```

### Research and verify

```text
Use basis in open-research mode to check this article. Prefer primary sources.
Treat anything you could not read as unverified. Today is the reference date
for current claims.

[paste article]
```

Open research requires an agent with retrieval tools. Basis never claims to have browsed a source when no such tool was available.

### Check a local document

```text
Use basis to audit docs/launch.md against docs/evidence/. Do not edit the file.
Return high-severity findings first.
```

To repair the file, explicitly say so:

```text
Use basis to repair docs/launch.md using docs/evidence/. Change factual prose
only. Write the full audit to launch-audit.json using the Basis JSON schema.
```

### Machine-readable output

```text
Use basis in JSON mode. Audit only; do not repair the text.

[paste draft and sources]
```

The output follows [`schemas/report.schema.json`](schemas/report.schema.json) and can be checked locally:

```bash
python3 scripts/validate-report.py report.json
```

## Evidence modes

| Mode | What Basis uses | What it must not imply |
| --- | --- | --- |
| **Provided sources** | Only material the user supplied or identified | That other research was performed |
| **Open research** | Sources found and actually read with available tools | That the search was comprehensive |
| **No sources** | Internal consistency, calculations, local files, and explicit gaps | That model memory is checked evidence |

## Claim statuses

| Status | Meaning |
| --- | --- |
| `supported` | Checked evidence establishes every material part, including scope and time frame. |
| `partially_supported` | Evidence establishes part of the claim, but an important element or qualifier is too strong or missing. |
| `contradicted` | Checked evidence directly conflicts with the claim. |
| `unsupported` | The checked evidence does not establish the claim. This does **not** mean it is false. |
| `unverified` | Accessible evidence was insufficient to check the claim. |
| `disputed` | Credible checked sources materially conflict. |

Severity is separate: `high`, `medium`, `low`, or `none`. A claim can be unsupported and low severity, or contradicted and high severity.

## How it works

1. **Extract claims.** Split compound statements while preserving qualifiers, dates, numbers, comparisons, and modality.
2. **Build a source ledger.** Record real sources, access status, type, date, and precise locations.
3. **Capture evidence.** Attach a verbatim quote, exact value, calculation, or executable result to each evidence-based verdict.
4. **Assign statuses.** Distinguish missing support, direct conflict, inaccessible evidence, and genuine disagreement.
5. **Run 24 checks.** Audit the claim itself, its citations, numbers, dates, reasoning, and consistency with the rest of the draft.
6. **Repair conservatively.** Narrow, attribute, correct, remove, or ask. Never invent a missing detail.
7. **Audit the audit.** Recheck quotations, calculations, entities, negations, repairs, and coverage limits.

Source text is always treated as untrusted data, not instructions. Private drafts are not sent to external services without explicit authorization.

## The 24 checks

### A. Claim-evidence fit

| # | Check | What it catches |
| --- | --- | --- |
| 1 | **Unsupported assertion** | A factual claim with no checked evidence behind it |
| 2 | **Partial support** | Evidence covers only part of a compound claim |
| 3 | **Contradicted claim** | Evidence directly reverses a value, date, actor, direction, or event |
| 4 | **Overgeneralized scope** | One sample, place, test, or period becomes a universal claim |
| 5 | **Inflated certainty** | Suggestive or conditional evidence becomes “proof” or a guarantee |
| 6 | **Speculation presented as fact** | A motive, prediction, explanation, or missing detail is asserted without support |

### B. Citations and quotations

| # | Check | What it catches |
| --- | --- | --- |
| 7 | **Unverifiable citation** | A reference or relevant passage cannot be found or accessed |
| 8 | **Citation supports a different claim** | A real source does not entail the statement beside it |
| 9 | **Misquotation** | Words, numbers, negation, or punctuation differ materially from the source |
| 10 | **Quotation out of context** | Exact words distort the source's larger position or conditions |
| 11 | **Misattribution** | The wrong person, institution, author, or publisher gets credit |
| 12 | **Secondary source presented as primary** | Reporting about evidence is treated as the original evidence |
| 13 | **Circular sourcing** | Repetition of one origin is counted as independent corroboration |

### C. Numbers and comparisons

| # | Check | What it catches |
| --- | --- | --- |
| 14 | **False precision** | Formatting creates accuracy the measurement or estimate does not have |
| 15 | **Arithmetic or unit error** | Wrong calculations, conversions, rates, units, or percentage-point language |
| 16 | **Missing baseline or denominator** | A number lacks the group, sample, period, or starting value needed to interpret it |
| 17 | **Misleading comparison** | Different definitions, periods, versions, or methods are compared as equivalent |

### D. Dates and freshness

| # | Check | What it catches |
| --- | --- | --- |
| 18 | **Time-frame drift** | Plans become outcomes, old results become current, or periods are merged |
| 19 | **Stale evidence for a current claim** | Old evidence is used for “now,” “latest,” or “currently” |

### E. Reasoning and attribution

| # | Check | What it catches |
| --- | --- | --- |
| 20 | **Correlation presented as causation** | Timing or covariance becomes a cause without adequate evidence |
| 21 | **Entity confusion** | Similar people, products, organizations, studies, or versions are mixed up |
| 22 | **Opinion or consensus presented as settled fact** | Value judgments or selected voices become universal agreement |
| 23 | **Absence of evidence presented as disproof** | A failed search or a source's silence becomes “never” or “disproven” |

### F. Draft consistency

| # | Check | What it catches |
| --- | --- | --- |
| 24 | **Internal contradiction** | Two passages, a summary and table, or a heading and section disagree |

An inaccessible link is not automatically fabricated. A missing citation is not automatically false. A citation is not automatically support. These distinctions are central to Basis.

## What Basis does not do

- It does not guarantee truth or replace expert review.
- It does not produce a numerical “truth score.”
- It does not use model memory as a checked citation.
- It does not call claims false merely because evidence was unavailable.
- It does not bypass paywalls, authentication, or access restrictions.
- It does not edit files unless asked.
- It does not fact-check fiction as though invented events were real.

For medical, legal, financial, safety, electoral, or reputational decisions, use qualified professional review in addition to an evidence audit.

## Repository layout

```text
basis/
├── SKILL.md                    # The portable agent instructions
├── schemas/report.schema.json  # Machine-readable audit contract
├── examples/                   # Fictional draft, sources, and valid report
├── evals/                      # Small development set and evaluation method
├── scripts/                    # Dependency-free package and report validators
├── tests/                      # Standard-library unit tests
├── agents/openai.yaml          # OpenAI-compatible agent metadata
├── .claude-plugin/             # Claude plug-in and marketplace manifests
└── .cursor-plugin/             # Cursor plug-in manifest
```

## Development

Basis has no build step and no runtime package dependencies. Python 3.10+ is enough for the local validators and tests.

```bash
python3 scripts/validate-package.py
python3 scripts/validate-report.py examples/report.json
python3 -m unittest discover -s tests -v
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`evals/README.md`](evals/README.md), and [`AGENTS.md`](AGENTS.md) before changing the skill.

## Roadmap

The initial release focuses on a careful, portable prompt and a strict report contract. Good next steps are:

- More adversarial evaluation cases, including prompt injection and conflicting sources.
- Public, reproducible comparisons against a generic fact-check prompt.
- Optional deterministic quotation matching for locally saved source text.
- Editorial integrations that consume the JSON report.
- Multilingual examples tested with native-speaking reviewers.

Performance claims belong in the README only after reproducible evaluation supports them.

## Inspiration

Basis is an independent project inspired by the focused, portable packaging of [blader/humanizer](https://github.com/blader/humanizer). Humanizer edits AI writing patterns; Basis audits claim-to-evidence fit and citation integrity. No performance or affiliation claim is implied.

## License

MIT. See [`LICENSE`](LICENSE).
