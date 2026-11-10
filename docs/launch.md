# Launch checklist

Basis is ready as a local project. Publishing and adoption still require a real repository owner, clean installation testing, and reproducible evidence of quality.

## 1. Claim the repository identity

1. Create a GitHub repository named `basis` under your account or organization. If the name is unavailable, choose one distinct name and update every manifest, command, `$basis` reference, and validator expectation.
2. Replace `YOUR_USERNAME` in `README.md`.
3. Add your real author name, repository URL, and homepage to the plug-in manifests.
4. Review `LICENSE` and `SECURITY.md` contact details.
5. Upload `assets/basis-social.png` as the repository social preview if desired. GitHub accepts PNG images and the file is already sized at 1280 × 640.

Suggested GitHub description:

> Evidence lint for AI writing: check claims, citations, quotes, numbers, and repairs against sources your agent actually read.

Suggested topics:

```text
agent-skill, ai-agents, fact-checking, citations, hallucination,
claude-code, codex, cursor, llm, writing
```

## 2. Verify before publishing

```bash
npm test
npx --yes skills@1.5.20 add . --list
claude plugin validate .
```

Then install from a clean checkout in each agent you claim to support. Test these paths:

- direct `/basis` invocation;
- provided-source audit with no web tool;
- audit-only file review with no file modification;
- explicit file repair;
- JSON output followed by local validation;
- a source containing a prompt-injection attempt;
- an inaccessible citation, ensuring it is not called fabricated.

Record actual compatibility results. Remove installation instructions for any path you cannot support.

## 3. Publish the initial release

1. Commit with a clear message such as `Initial Basis agent skill`.
2. Push the repository and confirm GitHub Actions passes.
3. Tag `v0.1.0` only after validation.
4. Create a release from `CHANGELOG.md` with install commands and the fictional example.
5. Test installation from the published repository, not just the local directory.

## 4. Earn attention with evidence

The strongest launch asset is a reproducible comparison, not a large claim.

- Build a held-out set of real or properly licensed examples with permission to publish.
- Include supported text as well as errors so the skill does not learn to flag everything.
- Compare Basis with a generic fact-check prompt using the same model and tools.
- Publish raw outputs, scoring rules, disagreements, and failures.
- Show a short before/after example with evidence links readers can inspect.
- Ask early users for failure cases and turn them into regression evals.

Do not buy stars, fabricate testimonials, spam unrelated repositories, or claim “99% accuracy.” A small, reproducible evaluation is more credible than an unexplained score.

## 5. Useful follow-up releases

Prioritize in this order:

1. Fix incorrect verdicts and invented evidence.
2. Add deterministic verbatim-quote checks for saved local sources.
3. Expand multilingual and high-stakes evaluation with qualified reviewers.
4. Add report viewers or editor integrations that consume the JSON contract.
5. Improve installation and documentation from actual user friction.

Keep the core skill portable. Put optional integrations in separate files so agents that do not need them do not pay their context cost.
