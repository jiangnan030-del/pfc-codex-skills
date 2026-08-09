#!/usr/bin/env python3
"""Query and validate the pinned pfc-code knowledge-base catalog."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "knowledge" / "pfc-code" / "catalog.json"
DEFAULT_LOCK = ROOT / "knowledge" / "pfc-code" / "source-lock.json"
HEX40 = re.compile(r"[0-9a-f]{40}")
VALID_PHASES = {"P1", "P2", "P3", "P4", "P5", "P6", "P7"}
REQUIRED_ENTRY_FIELDS = {
    "id",
    "title",
    "path",
    "sha",
    "dimension",
    "kind",
    "phases",
    "topics",
    "summary",
}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("missing file: {}".format(path)) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON in {}: {}".format(path, exc)) from exc


def validate(
    catalog: Dict[str, Any],
    lock: Dict[str, Any],
    local_root: Optional[Path] = None,
) -> List[str]:
    errors: List[str] = []
    source = catalog.get("source", {})
    commit = source.get("commit", "")
    if not HEX40.fullmatch(commit):
        errors.append("catalog source.commit must be a lowercase 40-character SHA")
    if commit != lock.get("commit"):
        errors.append("catalog and source-lock commits differ")
    if source.get("owner") != lock.get("owner") or source.get("repo") != lock.get("repo"):
        errors.append("catalog and source-lock repository identities differ")

    entries = catalog.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("catalog entries must be a non-empty list")
        return errors

    seen_ids: Set[str] = set()
    seen_paths: Set[str] = set()
    for index, entry in enumerate(entries, 1):
        prefix = "entry {}".format(index)
        if not isinstance(entry, dict):
            errors.append("{} must be an object".format(prefix))
            continue
        missing = REQUIRED_ENTRY_FIELDS - set(entry)
        if missing:
            errors.append(
                "{} missing fields: {}".format(prefix, ", ".join(sorted(missing)))
            )
            continue
        entry_id = entry["id"]
        path_text = entry["path"]
        if entry_id in seen_ids:
            errors.append("duplicate entry id: {}".format(entry_id))
        seen_ids.add(entry_id)
        if path_text in seen_paths:
            errors.append("duplicate entry path: {}".format(path_text))
        seen_paths.add(path_text)
        path = Path(path_text)
        if path.is_absolute() or ".." in path.parts:
            errors.append("{}: path must be repository-relative".format(entry_id))
        if not HEX40.fullmatch(entry["sha"]):
            errors.append("{}: sha must be a lowercase 40-character blob SHA".format(entry_id))
        if entry["dimension"] not in {"2d", "3d"}:
            errors.append("{}: dimension must be 2d or 3d".format(entry_id))
        phases = set(entry["phases"])
        if not phases or not phases <= VALID_PHASES:
            errors.append("{}: phases must be drawn from P1-P7".format(entry_id))
        if not isinstance(entry["topics"], list) or not entry["topics"]:
            errors.append("{}: topics must be a non-empty list".format(entry_id))
        if local_root is not None and not (local_root / path).is_file():
            errors.append(
                "{}: missing from local checkout: {}".format(entry_id, path_text)
            )
    return errors


def tokenise(text: str) -> List[str]:
    return [token for token in re.split(r"[^a-z0-9_+-]+", text.lower()) if token]


def score_entry(entry: Dict[str, Any], query_tokens: List[str]) -> int:
    if not query_tokens:
        return 1
    title_topics = " ".join([entry["title"]] + entry["topics"]).lower()
    body = " ".join([entry["path"], entry["summary"]] + entry["phases"]).lower()
    score = 0
    for token in query_tokens:
        if token in title_topics:
            score += 3
        if token in body:
            score += 1
    return score


def pinned_url(source: Dict[str, Any], path: str) -> str:
    base = "https://github.com/" + source["owner"] + "/" + source["repo"]
    return base + "/blob/" + source["commit"] + "/" + quote(path, safe="/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="", help="free-text topic query")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--source-lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--dimension", choices=["2d", "3d"])
    parser.add_argument("--kind", help="tutorial, example, verification, python, thermal, or coupling")
    parser.add_argument("--phase", choices=sorted(VALID_PHASES))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--check", action="store_true", help="validate metadata and exit")
    parser.add_argument("--local-root", type=Path, help="also verify paths in a local pfc-code checkout")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")

    try:
        catalog = load_json(args.catalog)
        lock = load_json(args.source_lock)
        errors = validate(catalog, lock, args.local_root)
    except ValueError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print("ERROR: {}".format(error), file=sys.stderr)
        return 1

    if args.check:
        print(
            "OK: {} entries pinned to {}".format(
                len(catalog["entries"]), catalog["source"]["commit"]
            )
        )
        return 0

    query_tokens = tokenise(args.query)
    matches: List[Tuple[int, Dict[str, Any]]] = []
    for entry in catalog["entries"]:
        if args.dimension and entry["dimension"] != args.dimension:
            continue
        if args.kind and entry["kind"] != args.kind:
            continue
        if args.phase and args.phase not in entry["phases"]:
            continue
        score = score_entry(entry, query_tokens)
        if query_tokens and score == 0:
            continue
        matches.append((score, entry))

    matches.sort(key=lambda item: (-item[0], item[1]["id"]))
    selected = [entry for _, entry in matches[: args.limit]]
    source = catalog["source"]

    if args.as_json:
        payload = {
            "source": source,
            "query": args.query,
            "filters": {
                "dimension": args.dimension,
                "kind": args.kind,
                "phase": args.phase,
            },
            "results": [
                dict(entry, url=pinned_url(source, entry["path"]))
                for entry in selected
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("pfc-code @ {}".format(source["commit"]))
    if not selected:
        print("No catalog matches.")
        return 0
    for entry in selected:
        tags = ", ".join([entry["dimension"], entry["kind"]] + entry["phases"])
        print("- {} [{}]".format(entry["title"], tags))
        print("  {}".format(entry["summary"]))
        print("  {}".format(pinned_url(source, entry["path"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
