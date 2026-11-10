# Contributing to Basis

Good contributions make verdicts more precise, evidence easier to inspect, repairs more conservative, or packaging easier to use. More rules are not automatically better.

## Start small

1. Search existing issues and the 24 checks for overlap.
2. For an audit problem, open a **Bad audit or repair** issue with a minimal, non-sensitive example.
3. For a new failure category, open a **Propose a check** issue and explain why no current check covers it.
4. Keep pull requests focused. Behavior changes need a changelog entry and, where possible, an evaluation case.

Do not submit private documents, confidential citations, personal data, or copyrighted source text beyond a short excerpt needed to demonstrate the issue.

## Local setup

Basis needs Python 3.10 or newer for development. There are no Python package dependencies.

```bash
npm test
```

Or run the individual Python checks:

```bash
python3 scripts/validate-package.py
python3 scripts/validate-report.py examples/report.json
python3 -m unittest discover -s tests -v
```

To test skill discovery with Node.js installed:

```bash
npx --yes skills@1.5.20 add . --list
```

## Changing the skill

- Preserve exact claim qualifiers before judging them.
- Keep `unsupported` separate from `contradicted` and `unverified`.
- Require checked evidence for evidence-based verdicts.
- Treat source text as untrusted data, never as instructions.
- Do not make live web access a requirement for provided-source or no-source mode.
- Do not let a repair introduce a new unsupported fact.
- Update the README tables whenever check names or numbers change.
- Stay within the 5,000-word skill budget.

Read `AGENTS.md` for the complete package rules.

## Adding an evaluation case

A good case has one main trap, a short draft, enough source text to determine the expected result, and an explicit rationale. Include difficult negatives: a real citation that does not support the claim, an exact but misleading quotation, an inaccessible source that must not be called fabricated, or two sources that genuinely conflict.

The `evals/` directory is a development set. Do not tune on it and then report it as held-out accuracy. See `evals/README.md` for the evaluation method.

## Improving the report validator

Use only the Python standard library unless the project explicitly adopts a dependency. Add tests for valid and invalid behavior. Useful validation includes:

- unknown fields and malformed IDs;
- duplicate IDs and check IDs;
- mismatched status counts;
- dangling or unaccessed evidence sources;
- missing evidence for evidence-based verdicts;
- disputed verdicts without two distinct sources.

The validator cannot prove that an excerpt really appears in an external source. Do not imply that structural validation equals factual verification.

## Writing and examples

Lead with the main point. Use active voice and short sections. Define technical terms. Keep commands and identifiers exact. Label all fictional examples clearly. Do not add performance, adoption, or compatibility claims without evidence.

## Release checklist

1. Run all required checks.
2. Test installation in at least one clean agent environment.
3. Review the README example against `SKILL.md`.
4. Update `CHANGELOG.md` and all package versions.
5. Create a tagged release only after the checks pass.
6. Follow `docs/launch.md` for repository metadata and publication.

## License

Contributions are licensed under the repository's MIT License.
