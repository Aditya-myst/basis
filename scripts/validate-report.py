#!/usr/bin/env python3
"""Validate Basis JSON reports using only the Python standard library."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
from typing import Any

SCHEMA_VERSION = "1.0"
MODES = {"provided-sources", "open-research", "no-sources"}
STATUSES = (
    "supported",
    "partially_supported",
    "contradicted",
    "unsupported",
    "unverified",
    "disputed",
)
SEVERITIES = {"none", "low", "medium", "high"}
SOURCE_KINDS = {
    "primary",
    "secondary",
    "tertiary",
    "dataset",
    "code",
    "other",
    "unknown",
}
EVIDENCE_KINDS = {"quotation", "data", "calculation", "output", "paraphrase"}
CLAIM_ID = re.compile(r"^C[1-9][0-9]*$")
SOURCE_ID = re.compile(r"^S[1-9][0-9]*$")


def _check_keys(
    value: Any,
    required: set[str],
    optional: set[str],
    path: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return False
    for key in sorted(required - value.keys()):
        errors.append(f"{path}.{key} is required")
    for key in sorted(value.keys() - required - optional):
        errors.append(f"{path}.{key} is not an allowed field")
    return True


def _nonempty_string(value: Any, path: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")
        return False
    return True


def _count(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append(f"{path} must be a non-negative integer")


def validate_report(report: Any) -> list[str]:
    """Return human-readable validation errors; an empty list means valid."""

    errors: list[str] = []
    top_fields = {
        "schema_version",
        "mode",
        "summary",
        "claims",
        "sources",
        "limitations",
        "revised_text",
    }
    if not _check_keys(report, top_fields, set(), "report", errors):
        return errors

    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"report.schema_version must be {SCHEMA_VERSION!r}")
    if report.get("mode") not in MODES:
        errors.append(f"report.mode must be one of {sorted(MODES)}")

    sources = report.get("sources")
    source_map: dict[str, dict[str, Any]] = {}
    if not isinstance(sources, list):
        errors.append("report.sources must be an array")
        sources = []
    for index, source in enumerate(sources):
        path = f"report.sources[{index}]"
        fields = {"id", "title", "locator", "accessed", "kind", "publication_date"}
        if not _check_keys(source, fields, set(), path, errors):
            continue
        source_id = source.get("id")
        if not isinstance(source_id, str) or not SOURCE_ID.fullmatch(source_id):
            errors.append(f"{path}.id must look like S1, S2, ...")
        elif source_id in source_map:
            errors.append(f"{path}.id duplicates {source_id}")
        else:
            source_map[source_id] = source
        _nonempty_string(source.get("title"), f"{path}.title", errors)
        _nonempty_string(source.get("locator"), f"{path}.locator", errors)
        if not isinstance(source.get("accessed"), bool):
            errors.append(f"{path}.accessed must be true or false")
        if source.get("kind") not in SOURCE_KINDS:
            errors.append(f"{path}.kind must be one of {sorted(SOURCE_KINDS)}")
        publication_date = source.get("publication_date")
        if publication_date is not None:
            _nonempty_string(publication_date, f"{path}.publication_date", errors)

    claims = report.get("claims")
    claim_ids: set[str] = set()
    actual_counts: Counter[str] = Counter()
    if not isinstance(claims, list):
        errors.append("report.claims must be an array")
        claims = []
    for index, claim in enumerate(claims):
        path = f"report.claims[{index}]"
        fields = {
            "id",
            "text",
            "status",
            "severity",
            "check_ids",
            "evidence",
            "explanation",
            "repair",
        }
        if not _check_keys(claim, fields, set(), path, errors):
            continue

        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not CLAIM_ID.fullmatch(claim_id):
            errors.append(f"{path}.id must look like C1, C2, ...")
        elif claim_id in claim_ids:
            errors.append(f"{path}.id duplicates {claim_id}")
        else:
            claim_ids.add(claim_id)
        label = claim_id if isinstance(claim_id, str) else path

        _nonempty_string(claim.get("text"), f"{path}.text", errors)
        _nonempty_string(claim.get("explanation"), f"{path}.explanation", errors)
        repair = claim.get("repair")
        if repair is not None:
            _nonempty_string(repair, f"{path}.repair", errors)

        status = claim.get("status")
        if status not in STATUSES:
            errors.append(f"{path}.status must be one of {list(STATUSES)}")
        else:
            actual_counts[status] += 1
        severity = claim.get("severity")
        if severity not in SEVERITIES:
            errors.append(f"{path}.severity must be one of {sorted(SEVERITIES)}")
        if status == "supported":
            if severity != "none":
                errors.append(f"{label}: supported claims must have severity 'none'")
            if claim.get("check_ids") != []:
                errors.append(f"{label}: supported claims cannot list defect check IDs")
        elif status in STATUSES and severity == "none":
            errors.append(f"{label}: a non-supported claim needs a severity other than 'none'")

        check_ids = claim.get("check_ids")
        if not isinstance(check_ids, list):
            errors.append(f"{path}.check_ids must be an array")
        else:
            for check_id in check_ids:
                if (
                    isinstance(check_id, bool)
                    or not isinstance(check_id, int)
                    or not 1 <= check_id <= 24
                ):
                    errors.append(f"{path}.check_ids contains invalid check {check_id!r}")
            if len(set(check_ids)) != len(check_ids):
                errors.append(f"{path}.check_ids must not contain duplicates")

        evidence = claim.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{path}.evidence must be an array")
            evidence = []
        evidence_sources: set[str] = set()
        for evidence_index, item in enumerate(evidence):
            evidence_path = f"{path}.evidence[{evidence_index}]"
            evidence_fields = {"source_id", "kind", "excerpt", "locator"}
            if not _check_keys(item, evidence_fields, set(), evidence_path, errors):
                continue
            source_id = item.get("source_id")
            if not isinstance(source_id, str) or not SOURCE_ID.fullmatch(source_id):
                errors.append(f"{evidence_path}.source_id must look like S1, S2, ...")
            elif source_id not in source_map:
                errors.append(f"{evidence_path}.source_id references unknown source {source_id}")
            else:
                evidence_sources.add(source_id)
                if not source_map[source_id].get("accessed"):
                    errors.append(
                        f"{evidence_path}.source_id references unaccessed source {source_id}"
                    )
            if item.get("kind") not in EVIDENCE_KINDS:
                errors.append(
                    f"{evidence_path}.kind must be one of {sorted(EVIDENCE_KINDS)}"
                )
            _nonempty_string(item.get("excerpt"), f"{evidence_path}.excerpt", errors)
            _nonempty_string(item.get("locator"), f"{evidence_path}.locator", errors)

        if status in {"supported", "partially_supported", "contradicted"} and not evidence:
            errors.append(f"{label}: {status} claims need at least one evidence item")
        if status == "unverified" and evidence:
            errors.append(f"{label}: unverified claims cannot cite checked evidence as a verdict")
        if status == "disputed" and len(evidence_sources) < 2:
            errors.append(f"{label}: disputed claims need evidence from at least two sources")

    summary = report.get("summary")
    if _check_keys(summary, {"counts"}, set(), "report.summary", errors):
        counts = summary.get("counts")
        if _check_keys(counts, set(STATUSES), set(), "report.summary.counts", errors):
            for status in STATUSES:
                _count(counts.get(status), f"report.summary.counts.{status}", errors)
                if counts.get(status) != actual_counts[status]:
                    errors.append(
                        f"report.summary.counts.{status} is {counts.get(status)!r}; "
                        f"claims contain {actual_counts[status]}"
                    )

    limitations = report.get("limitations")
    if not isinstance(limitations, list):
        errors.append("report.limitations must be an array")
    else:
        for index, limitation in enumerate(limitations):
            _nonempty_string(limitation, f"report.limitations[{index}]", errors)

    revised_text = report.get("revised_text")
    if revised_text is not None and not isinstance(revised_text, str):
        errors.append("report.revised_text must be a string or null")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="+", type=Path, help="Basis JSON report(s)")
    args = parser.parse_args()
    failed = False

    for path in args.reports:
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except OSError as error:
            print(f"{path}: cannot read file: {error}", file=sys.stderr)
            failed = True
            continue
        except json.JSONDecodeError as error:
            print(f"{path}: invalid JSON: {error}", file=sys.stderr)
            failed = True
            continue

        errors = validate_report(report)
        if errors:
            failed = True
            for error in errors:
                print(f"{path}: {error}", file=sys.stderr)
        else:
            print(
                f"{path}: valid Basis report "
                f"({len(report['claims'])} claims, {len(report['sources'])} sources)"
            )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
