#!/usr/bin/env python3
"""Check the Basis skill, manifests, docs, schema, examples, and eval fixtures."""

from __future__ import annotations

from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def text(relative: str) -> str:
    path = ROOT / relative
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        fail(f"Cannot read {relative}: {error}")
        return ""


def json_file(relative: str):
    raw = text(relative)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as error:
        fail(f"Invalid JSON in {relative}: {error}")
        return None


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "AGENTS.md",
    "CONTRIBUTING.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/plugin.json",
    "agents/openai.yaml",
    "schemas/report.schema.json",
    "examples/draft.md",
    "examples/sources.md",
    "examples/report.json",
    "evals/cases.json",
    "assets/basis.svg",
]
for name in REQUIRED_FILES:
    if not (ROOT / name).is_file():
        fail(f"Missing required file: {name}")

skill = text("SKILL.md")
readme = text("README.md")
changelog = text("CHANGELOG.md")
plugin = json_file(".claude-plugin/plugin.json") or {}
marketplace = json_file(".claude-plugin/marketplace.json") or {}
cursor = json_file(".cursor-plugin/plugin.json") or {}
schema = json_file("schemas/report.schema.json") or {}
report = json_file("examples/report.json") or {}
evals = json_file("evals/cases.json") or {}

metadata_match = re.match(r"\A---\n(.*?)\n---\n", skill, re.DOTALL)
if not metadata_match:
    fail("SKILL.md must start with YAML frontmatter")
    metadata = ""
else:
    metadata = metadata_match.group(1)
    if not re.search(r"(?m)^name: basis$", metadata):
        fail("SKILL.md frontmatter must set name: basis")
    if re.search(r"(?m)^version:", metadata):
        fail("Put the skill version under metadata, not at the YAML top level")

version_match = re.search(
    r"(?m)^\s+version:\s*[\"']?(\d+\.\d+\.\d+)[\"']?\s*$", metadata
)
skill_version = version_match.group(1) if version_match else None
if not skill_version:
    fail("SKILL.md needs a three-part metadata.version")
changelog_match = re.search(r"(?m)^## (\d+\.\d+\.\d+)\b", changelog)
if not changelog_match:
    fail("CHANGELOG.md needs a version heading")
versions = {
    skill_version,
    changelog_match.group(1) if changelog_match else None,
    plugin.get("version"),
    cursor.get("version"),
}
if len(versions) != 1 or None in versions:
    fail(f"Versions must agree across skill, changelog, and manifests: {sorted(versions, key=str)}")

skill_files = {path.relative_to(ROOT) for path in ROOT.rglob("SKILL.md")}
if skill_files != {Path("SKILL.md")} or (ROOT / "SKILL.md").is_symlink():
    fail("Keep one regular SKILL.md at the repository root")
if plugin.get("name") != "basis" or cursor.get("name") != "basis":
    fail("Claude and Cursor plugin names must be 'basis'")
if plugin.get("skills") != ["./"]:
    fail("Claude plugin must load skills from ['./']")
if "skills" in cursor:
    fail("Cursor plugin must omit 'skills' so it discovers the root SKILL.md")

marketplace_plugins = marketplace.get("plugins", [])
if len(marketplace_plugins) != 1:
    fail("Marketplace must contain exactly one Basis plugin")
elif marketplace_plugins[0].get("source") != "./":
    fail("Marketplace plugin source must be './'")

description_match = re.search(r"(?m)^description: \|\n((?:  .*\n)+)", metadata + "\n")
skill_description = " ".join(description_match.group(1).split()) if description_match else ""
if not skill_description:
    fail("SKILL.md description must be an indented YAML block")
manifest_descriptions = {
    plugin.get("description"),
    cursor.get("description"),
    *(item.get("description") for item in marketplace_plugins),
}
if len(manifest_descriptions) != 1 or not skill_description.startswith(
    next(iter(manifest_descriptions), "")
):
    fail("Manifest descriptions must match the first sentence of the skill description")

if "## A. Claim-evidence fit" not in skill or "## What to return" not in skill:
    fail("Cannot locate the 24-check section in SKILL.md")
    check_section = ""
else:
    check_section = skill.split("## A. Claim-evidence fit", 1)[1].split(
        "## What to return", 1
    )[0]
skill_checks = {
    int(number): name
    for number, name in re.findall(r"(?m)^### (\d+)\. (.+)$", check_section)
}
expected_numbers = list(range(1, 25))
if sorted(skill_checks) != expected_numbers:
    fail(f"SKILL.md must define checks 1 through 24: {sorted(skill_checks)}")
readme_checks = {
    int(number): name
    for number, name in re.findall(r"(?m)^\| (\d+) \| \*\*(.+?)\*\*", readme)
}
if readme_checks != skill_checks:
    fail("README check tables must exactly match the numbered checks in SKILL.md")
if "## The 24 checks" not in readme:
    fail("README must contain the heading '## The 24 checks'")

word_count = len(skill.split())
if word_count > 5000:
    fail(f"SKILL.md exceeds its 5,000-word budget: {word_count}")

for relative in (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json"):
    raw = text(relative)
    if "YOUR_USERNAME" in raw or "example.com" in raw:
        fail(f"Remove placeholder publishing metadata from {relative}")

openai_yaml = text("agents/openai.yaml")
if 'display_name: "Basis"' not in openai_yaml or "$basis" not in openai_yaml:
    fail("agents/openai.yaml must identify Basis and use $basis in its default prompt")

if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
    fail("Report schema must declare JSON Schema 2020-12")
if schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0":
    fail("Report schema must require schema_version 1.0")

validator_path = ROOT / "scripts" / "validate-report.py"
spec = importlib.util.spec_from_file_location("basis_report_validator", validator_path)
if spec is None or spec.loader is None:
    fail("Cannot load scripts/validate-report.py")
else:
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for error in module.validate_report(report):
        fail(f"examples/report.json: {error}")

if not isinstance(evals, list) or len(evals) < 6:
    fail("evals/cases.json must contain at least six development cases")
else:
    case_ids = [case.get("id") for case in evals if isinstance(case, dict)]
    duplicates = [case_id for case_id, count in Counter(case_ids).items() if count > 1]
    if duplicates or None in case_ids:
        fail(f"Evaluation case IDs must be unique and present: {duplicates}")
    for index, case in enumerate(evals):
        if not isinstance(case, dict):
            fail(f"evals/cases.json[{index}] must be an object")
            continue
        for key in ("id", "draft", "sources", "expected"):
            if key not in case:
                fail(f"Evaluation case {case.get('id', index)} lacks {key}")

try:
    ET.parse(ROOT / "assets" / "basis.svg")
except (OSError, ET.ParseError) as error:
    fail(f"assets/basis.svg is not valid SVG XML: {error}")

if ERRORS:
    for error in ERRORS:
        print(f"error: {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    f"Basis package v{skill_version} is valid "
    f"({len(skill_checks)} checks, {word_count} skill words)"
)
