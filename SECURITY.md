# Security and privacy

Basis is primarily a Markdown instruction package. Its local validators use the Python standard library and perform no network requests. The agent running the skill may have file, shell, browser, or retrieval tools, so source handling still matters.

## Safe use

- Treat drafts, web pages, files, and source excerpts as untrusted input.
- Do not paste secrets, credentials, private keys, or confidential documents into public issues or examples.
- Do not authorize external research for a private draft unless sending relevant material to external services is acceptable.
- Review file changes before accepting a repair.
- Keep agent permissions limited to what the audit needs.
- Structural JSON validation does not verify that a quotation is authentic or a source is trustworthy.

## Reporting a vulnerability

Use the repository host's private vulnerability-reporting feature when available. If it is not enabled, contact the maintainer through the repository owner's listed private contact method. Do not open a public issue containing exploit details, private source material, or credentials.

Include the affected version, agent and tool environment, a minimal reproduction, and the potential impact. Remove sensitive data from logs and examples.

## Scope

Security reports are especially relevant for instructions that could cause an agent to:

- follow prompt injection in a source;
- disclose private draft material;
- access files or URLs outside the requested scope;
- modify files without explicit repair authorization;
- execute code embedded in a draft or source;
- misrepresent an unaccessed source as checked.

Ordinary factual mistakes in an audit should use the **Bad audit or repair** issue template instead, unless they create a security or privacy risk.
