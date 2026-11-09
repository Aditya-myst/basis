# Basis

### Check whether AI citations actually support their claims.

Basis is a free, open-source agent skill for auditing factual writing against sources the AI actually read. It finds unsupported claims, misleading quotations, citation mismatches, numerical errors, stale evidence, and causal overreach—then repairs only what the evidence allows.

**No invented sources. No unexplained truth score. No “false” verdict merely because evidence is missing.**

```text
A real-looking citation does not necessarily support the sentence beside it.
Basis checks the claim, shows the evidence, and limits the repair.
```

## See what it does

This fictional draft contains a subtle misquotation and an unsupported causal claim:

> In a 2024 lab test, the Aero One lasted 22 hours, so it delivers all-day battery life in every situation. A reviewer called it “the best battery we've tested.” Unit sales rose from 10,000 to 20,000 after launch, proving the battery drove growth.

Basis checks the draft against three supplied sources and returns:

| Claim | Verdict | Why |
| --- | --- | --- |
| 22-hour battery test | `partially_supported` | The source specifies a prototype, video playback, and 150-nit brightness |
| All-day battery in every situation | `unsupported` | One video test does not cover every workload |
| “The best battery we've tested” | `contradicted` | The review says “among the longest-lasting” and limits the comparison to that year |
| Unit sales rose from 10,000 to 20,000 | `supported` | The values and direction match the report |
| The battery caused sales growth | `unsupported` | A concurrent marketing campaign was not controlled for |

**Concise repair**

> In a November 2024 lab test, an Aero One prototype played video for 22 hours at 150 nits. A reviewer placed it among the longest-lasting batteries tested that year. Unit sales doubled after launch, but the source does not isolate the battery's effect from a concurrent marketing campaign.

The full example is in [`examples/`](examples/). Ask for a **full ledger** when you want every claim, exact evidence excerpt, check ID, and coverage limitation.

## Install with npm / npx

Node.js 22 or newer includes npm and `npx`. You do **not** need to run `npm install` in this repository.

### Install for supported agents

Replace `YOUR_USERNAME` with your GitHub username:

```bash
npx --yes skills@1.5.20 add YOUR_USERNAME/basis --global --agent '*'
```

On Windows PowerShell, use `npx.cmd`:

```powershell
npx.cmd --yes skills@1.5.20 add YOUR_USERNAME/basis --global --agent '*'
```

The Skills CLI installs Basis for supported agents. Leave off `--global` to install it only in the current project.

### Codex

```bash
npx --yes skills@1.5.20 add YOUR_USERNAME/basis --global --agent codex
```

### Claude Code through the Skills CLI

```bash
npx --yes skills@1.5.20 add YOUR_USERNAME/basis --global --agent claude-code
```

### Claude Code plug-in

Inside Claude Code:

```text
/plugin marketplace add YOUR_USERNAME/basis
/plugin install basis@basis
```

The plug-in responds to `/basis:basis`.

### Install from a local checkout

```bash
git clone https://github.com/YOUR_USERNAME/basis.git
cd basis
npx --yes skills@1.5.20 add . --global --agent '*'
```

**Important:** npm installs the instructions; it does not provide an AI model. You need a compatible agent with model access, or you can use the free-chat method below.

## Use without an agent, subscription, or API key

You can use Basis in a free AI web chat that accepts long messages. npm is optional for this method.

1. Open `SKILL.md` and copy its complete contents.
2. Start a new AI chat.
3. Paste the skill with this instruction:

```text
Use the following Markdown document as the operating instructions for this
conversation. It defines a skill called Basis. Do not audit the instructions
themselves. Wait for my draft and sources.

[PASTE SKILL.md HERE]
```

4. Send your draft and evidence:

```text
Use Basis in provided-sources mode.

Give me a concise audit and repaired text. Use only the supplied evidence.
Do not invent missing information or treat model memory as a checked source.

DRAFT:
[Paste your text]

SOURCE S1:
[Paste the first relevant source or excerpt]

SOURCE S2:
[Paste the second relevant source or excerpt]
```

Providing source text is more reliable than providing only URLs when the chat cannot open links. Do not paste confidential material into a public or free chat service.

## Use with an installed agent

### Concise audit and repair

```text
Use basis in provided-sources mode.

Give me a concise findings table and repaired text. Use only the supplied
sources. Return high-severity findings first.

DRAFT:
[Paste your text]

SOURCES:
[Paste source text, paths, or URLs]
```

### Full claim ledger

```text
Use basis in provided-sources mode.
Return the full claim ledger with exact evidence excerpts.
Audit only; do not rewrite.

DRAFT:
[Paste your text]

SOURCES:
[Paste your evidence]
```

### Audit a local document

```text
Use basis to audit docs/launch.md against docs/evidence/.
Do not edit any files. Return a concise audit.
```

To permit edits, explicitly ask:

```text
Use basis to repair docs/launch.md using docs/evidence/.
Change factual prose only. Write the full audit to launch-audit.json.
```

### Open research

```text
Use basis in open-research mode to verify this article.
Prefer primary sources and record only sources you actually read.
Treat inaccessible evidence as unverified.

[Paste article]
```

Open research requires retrieval tools. Basis must not claim to have browsed a source when retrieval was unavailable.

## Evidence modes and verdicts

| Mode | Evidence used |
| --- | --- |
| `provided-sources` | Only sources the user supplied or identified |
| `open-research` | Sources found and actually read with available tools |
| `no-sources` | Internal consistency, calculations, local evidence, and explicit gaps |

| Status | Meaning |
| --- | --- |
| `supported` | Checked evidence establishes every material part of the claim |
| `partially_supported` | Evidence establishes only part of the claim or requires stronger limits |
| `contradicted` | Checked evidence directly conflicts with the claim |
| `unsupported` | Checked evidence does not establish the claim; this does not mean it is false |
| `unverified` | Accessible evidence was insufficient to check the claim |
| `disputed` | Credible checked sources materially conflict |

Severity is reported separately as `high`, `medium`, `low`, or `none`.

## Why Basis?

Generic fact-check prompts often:

- Treat a real-looking citation as proof without reading it
- Confuse missing support with direct contradiction
- Repair one invented fact by adding another
- Count repeated reporting as independent confirmation
- Return an accuracy percentage with no defensible method
- Hide research limits behind polished copy

Basis separates **claim extraction**, **source access**, **exact evidence**, **verdict**, and **repair**. Drafts and sources are treated as untrusted data, not instructions. Private material is not sent to external services without authorization.

## Machine-readable audits

Ask for JSON mode:

```text
Use basis in JSON mode.
Audit only; do not repair the text.

[Paste draft and sources]
```

Validate the resulting `report.json` locally:

```bash
python3 scripts/validate-report.py report.json
```

PowerShell:

```powershell
python scripts/validate-report.py report.json
```

The validator rejects unknown source references, evidence from unaccessed sources, mismatched counts, unsupported schema fields, missing evidence for evidence-based verdicts, and disputed claims backed by fewer than two sources.

Structural validation does not independently prove that an excerpt is authentic or a verdict is correct.

## The 24 checks

<details>
<summary><strong>Expand the complete evidence-check reference</strong></summary>

### A. Claim-evidence fit

| # | Check | What it catches |
| --- | --- | --- |
| 1 | **Unsupported assertion** | A factual claim with no checked evidence behind it |
| 2 | **Partial support** | Evidence covers only part of a compound claim |
| 3 | **Contradicted claim** | Evidence directly reverses a value, date, actor, direction, or event |
| 4 | **Overgeneralized scope** | One sample, place, test, or period becomes a universal claim |
| 5 | **Inflated certainty** | Suggestive or conditional evidence becomes proof or a guarantee |
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
| 19 | **Stale evidence for a current claim** | Old evidence is used for now, latest, or currently |

### E. Reasoning and attribution

| # | Check | What it catches |
| --- | --- | --- |
| 20 | **Correlation presented as causation** | Timing or covariance becomes a cause without adequate evidence |
| 21 | **Entity confusion** | Similar people, products, organizations, studies, or versions are mixed up |
| 22 | **Opinion or consensus presented as settled fact** | Value judgments or selected voices become universal agreement |
| 23 | **Absence of evidence presented as disproof** | A failed search or a source's silence becomes never or disproven |

### F. Draft consistency

| # | Check | What it catches |
| --- | --- | --- |
| 24 | **Internal contradiction** | Two passages, a summary and table, or a heading and section disagree |

</details>

## What Basis does not do

- It does not guarantee truth or replace expert review.
- It does not supply an AI model through npm.
- It does not use model memory as a checked citation.
- It does not call claims false merely because evidence was unavailable.
- It does not bypass paywalls, authentication, or access restrictions.
- It does not edit files unless explicitly asked.
- It does not produce a numerical truth score.

Medical, legal, financial, safety, electoral, and reputational decisions still require qualified professional review.

## Development

Basis has no build step and no runtime package dependencies. Python 3.10+ runs the validators and tests:

```bash
python3 scripts/validate-package.py
python3 scripts/validate-report.py examples/report.json
python3 -m unittest discover -s tests -v
```

On Windows, use `python` instead of `python3`.

```text
SKILL.md                    Portable agent instructions
schemas/report.schema.json  JSON audit contract
examples/                   Fictional worked example
scripts/                    Package and report validators
tests/                      Standard-library unit tests
evals/                      Development cases and evaluation method
docs/launch.md              Publishing and launch checklist
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), and [`AGENTS.md`](AGENTS.md).

## Inspiration and license

Basis is an independent project inspired by the focused, portable packaging of [blader/humanizer](https://github.com/blader/humanizer). Humanizer edits AI writing patterns; Basis audits claim-to-evidence fit and citation integrity. No affiliation or performance claim is implied.

MIT License. See [`LICENSE`](LICENSE).
