from __future__ import annotations

import argparse
import fnmatch
import re
import zipfile
from pathlib import Path

from clarify_to_act.io import write_text
from clarify_to_act.metrics import markdown_table
from make_supplement_package import collect_files, excluded, missing_required


FORBIDDEN_PATH_PATTERNS = [
    "*/__pycache__/*",
    "*.pyc",
    "*.pyo",
    ".git/*",
    ".agents/*",
    ".codex/*",
    "*apikey*",
    "*.aux",
    "*.blg",
    "*.fdb_latexmk",
    "*.fls",
    "*.log",
    "paper/clarify_to_act_supplement.zip",
    "data/generated/smoke_episodes.jsonl",
    "data/runs/api_smoke*.jsonl",
    "data/runs/smoke_*.jsonl",
    "data/runs/api_eval_100_results.jsonl",
    "data/runs/api_second_model_viability_results.jsonl",
    "paper/tables/api_smoke*",
    "paper/tables/smoke*",
    "paper/tables/api_eval_100/*",
    "paper/tables/api_eval_100_results.md",
    "paper/tables/api_second_model_viability_results.md",
]

FORBIDDEN_TEXT_PATTERNS = [
    ("OpenAI-style secret key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("local home path", re.compile("/" + "home/eston")),
    ("local API key path", re.compile("colm_workshop/" + r"apikey\.txt")),
]

BINARY_SUFFIXES = {".pdf", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".woff", ".ttf", ".pfb"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", default="paper/clarify_to_act_supplement.zip")
    parser.add_argument("--out", default="paper/supplement_audit.md")
    return parser.parse_args()


def path_matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def scan_text_file(path: Path) -> list[str]:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    hits = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            hits.append(label)
    return hits


def archive_rows(archive_path: Path, intended_files: list[Path]) -> tuple[list[list[str]], list[str]]:
    if not archive_path.exists():
        return [["Archive exists", "FAIL", str(archive_path)]], ["archive missing"]
    bad = []
    intended_names = {path.as_posix() for path in intended_files}
    with zipfile.ZipFile(archive_path) as zf:
        names = set(zf.namelist())
        forbidden = [name for name in names if path_matches(name, FORBIDDEN_PATH_PATTERNS)]
        missing = sorted(intended_names - names)
        extra = sorted(names - intended_names)
        if forbidden:
            bad.extend(f"forbidden archive path: {name}" for name in forbidden)
        if missing:
            bad.extend(f"missing archive path: {name}" for name in missing)
        if extra:
            bad.extend(f"extra archive path: {name}" for name in extra)
        rows = [
            ["Archive exists", "PASS", archive_path.as_posix()],
            ["Archive entries", "PASS", str(len(names))],
            ["Archive matches intended file list", "PASS" if not missing and not extra else "FAIL", f"missing={len(missing)}, extra={len(extra)}"],
            ["Forbidden archive paths", "PASS" if not forbidden else "FAIL", str(len(forbidden))],
            ["Archive excludes itself", "PASS" if archive_path.as_posix() not in names else "FAIL", archive_path.as_posix()],
        ]
    return rows, bad


def main() -> None:
    args = parse_args()
    out_path = Path(args.out)
    archive_path = Path(args.archive)

    files = sorted(set(collect_files()) | {out_path}, key=lambda path: path.as_posix())
    included = {path.as_posix() for path in files}
    missing = missing_required(files)
    forbidden_paths = [path.as_posix() for path in files if path_matches(path.as_posix(), FORBIDDEN_PATH_PATTERNS)]
    excluded_violations = [path.as_posix() for path in files if excluded(path.as_posix())]
    content_hits = []
    for path in files:
        if path == out_path:
            continue
        hits = scan_text_file(path)
        for hit in hits:
            content_hits.append([path.as_posix(), hit])

    archive_check_rows, archive_bad = archive_rows(archive_path, files)
    status_ok = not missing and not forbidden_paths and not excluded_violations and not content_hits and not archive_bad

    summary_rows = [
        ["Overall release audit", "PASS" if status_ok else "FAIL", "all checks clean" if status_ok else "one or more checks failed"],
        ["Intended package files", "PASS", str(len(files))],
        ["Missing required files", "PASS" if not missing else "FAIL", "none" if not missing else ", ".join(missing)],
        ["Forbidden intended paths", "PASS" if not forbidden_paths else "FAIL", str(len(forbidden_paths))],
        ["Excluded-path violations", "PASS" if not excluded_violations else "FAIL", str(len(excluded_violations))],
        ["Forbidden text hits", "PASS" if not content_hits else "FAIL", str(len(content_hits))],
    ]

    forbidden_path_rows = [[path] for path in forbidden_paths] or [["none"]]
    excluded_rows = [[path] for path in excluded_violations] or [["none"]]
    content_rows = content_hits or [["none", "none"]]
    missing_rows = [[path] for path in missing] or [["none"]]

    text = "\n".join(
        [
            "# Supplement Release Audit",
            "",
            "This generated audit checks the intended release supplement for forbidden files, local paths, API-key-like secrets, and stale development traces.",
            "",
            "## Summary",
            "",
            markdown_table(["Check", "Status", "Detail"], summary_rows),
            "## Archive Checks",
            "",
            markdown_table(["Check", "Status", "Detail"], archive_check_rows),
            "## Missing Required Files",
            "",
            markdown_table(["Path"], missing_rows),
            "## Forbidden Intended Paths",
            "",
            markdown_table(["Path"], forbidden_path_rows),
            "## Excluded-Path Violations",
            "",
            markdown_table(["Path"], excluded_rows),
            "## Forbidden Text Hits",
            "",
            markdown_table(["Path", "Pattern"], content_rows),
            "## Notes",
            "",
            "- API response caches are included as evidence, but API keys are excluded.",
            "- Binary files are checked by path and archive membership; text-pattern scanning is applied to UTF-8 readable files.",
            "- The audit is generated before the final deterministic zip is rebuilt, then rechecked by validation commands.",
            "",
            f"Overall status: **{'PASS' if status_ok else 'FAIL'}**",
        ]
    )
    write_text(out_path, text)
    print(f"wrote supplement release audit to {out_path}")
    print(f"overall status: {'PASS' if status_ok else 'FAIL'}")
    if not status_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
