from __future__ import annotations

import argparse
import fnmatch
import zipfile
from pathlib import Path

from clarify_to_act.io import write_text


FIXED_ZIP_TIMESTAMP = (2026, 6, 27, 0, 0, 0)

ROOT_FILES = [
    "README.md",
    "RESULTS_SUMMARY.md",
    "requirements.txt",
]

EXPLICIT_FILES = [
    "data/generated/episodes.jsonl",
    "data/generated/style_stress_episodes.jsonl",
    "data/generated/ambiguity_mix_shift_episodes.jsonl",
    "data/runs/offline_results.jsonl",
    "data/runs/ambiguity_mix_shift_results.jsonl",
    "data/runs/api_eval_100_corrected_results.jsonl",
    "data/runs/api_eval_100_cot_results.jsonl",
    "data/runs/api_style_stress_50_results.jsonl",
    "data/runs/api_second_model_25_results.jsonl",
    "data/runs/api_gpt_5_4_mini_test100_results.jsonl",
    "data/runs/api_gpt_5_5_test100_results.jsonl",
    "data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl",
    "data/runs/api_cache.jsonl",
    "data/runs/api_second_model_cache.jsonl",
    "data/runs/api_gpt_5_4_mini_cache.jsonl",
    "data/runs/api_gpt_5_5_cache.jsonl",
    "data/runs/api_gpt_5_4_mini_scene_cache.jsonl",
    "paper/README.md",
    "paper/clarify_to_act_paper_draft.md",
    "paper/dataset_card.md",
    "paper/references.md",
    "paper/claim_verification.md",
    "paper/claim_scope.md",
    "paper/paper_consistency_audit.md",
    "paper/reproducibility.md",
    "paper/submission_readiness.md",
    "paper/supplement_manifest.md",
    "paper/supplement_audit.md",
    "paper/latex/Makefile",
    "paper/latex/README.md",
    "paper/latex/main.tex",
    "paper/latex/refs.bib",
    "paper/latex/colm2026_conference.sty",
    "paper/latex/colm2026_conference.bst",
    "paper/latex/colm2026_conference.pdf",
    "paper/latex/fancyhdr.sty",
    "paper/latex/natbib.sty",
    "paper/latex/math_commands.tex",
    "paper/latex/main.bbl",
    "paper/latex/main.pdf",
]

INCLUDE_DIRS = [
    "src",
    "prompts",
    "tests",
    "paper/tables",
    "paper/figures",
    "paper/audits",
]

EXCLUDE_PATTERNS = [
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
    "data/runs/api_gpt_*_smoke*.jsonl",
    "data/runs/smoke_*.jsonl",
    "data/runs/api_eval_100_results.jsonl",
    "data/runs/api_second_model_viability_results.jsonl",
    "paper/tables/api_smoke*",
    "paper/tables/api_gpt_*_smoke*",
    "paper/tables/smoke*",
    "paper/tables/api_eval_100/*",
    "paper/tables/api_eval_100_results.md",
    "paper/tables/api_second_model_viability_results.md",
]

REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "src/run_experiment.py",
    "src/run_api_experiment.py",
    "src/verify_claims.py",
    "prompts/direct_act.txt",
    "tests/test_core_invariants.py",
    "data/generated/episodes.jsonl",
    "data/generated/style_stress_episodes.jsonl",
    "data/generated/ambiguity_mix_shift_episodes.jsonl",
    "data/runs/offline_results.jsonl",
    "data/runs/ambiguity_mix_shift_results.jsonl",
    "data/runs/api_eval_100_corrected_results.jsonl",
    "data/runs/api_eval_100_cot_results.jsonl",
    "data/runs/api_style_stress_50_results.jsonl",
    "data/runs/api_second_model_25_results.jsonl",
    "data/runs/api_gpt_5_4_mini_test100_results.jsonl",
    "data/runs/api_gpt_5_5_test100_results.jsonl",
    "data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl",
    "data/runs/api_cache.jsonl",
    "data/runs/api_second_model_cache.jsonl",
    "data/runs/api_gpt_5_4_mini_cache.jsonl",
    "data/runs/api_gpt_5_5_cache.jsonl",
    "data/runs/api_gpt_5_4_mini_scene_cache.jsonl",
    "paper/latex/main.tex",
    "paper/latex/main.pdf",
    "paper/latex/colm2026_conference.sty",
    "paper/latex/colm2026_conference.bst",
    "paper/latex/fancyhdr.sty",
    "paper/latex/natbib.sty",
    "paper/latex/math_commands.tex",
    "paper/reproducibility.md",
    "paper/claim_verification.md",
    "paper/paper_consistency_audit.md",
    "paper/dataset_card.md",
    "paper/tables/ambiguity_mix_shift.md",
    "paper/tables/ambiguity_utility_diagnostic.md",
    "paper/tables/situated_contrast_analysis.md",
    "paper/tables/clamber_external_sanity.md",
    "paper/tables/simulated_user_audit.md",
    "paper/tables/api_cache_replay_verification.md",
    "paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md",
    "paper/tables/api_eval_100_corrected/subset_stability.md",
    "paper/tables/api_eval_100_corrected/utility_sensitivity.md",
    "paper/claim_scope.md",
    "paper/submission_readiness.md",
    "paper/supplement_audit.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="paper/clarify_to_act_supplement.zip")
    parser.add_argument("--manifest", default="paper/supplement_manifest.md")
    parser.add_argument("--manifest-only", action="store_true")
    return parser.parse_args()


def excluded(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in EXCLUDE_PATTERNS)


def collect_files() -> list[Path]:
    files: set[Path] = set()
    for name in ROOT_FILES + EXPLICIT_FILES:
        path = Path(name)
        if path.exists() and not excluded(path.as_posix()):
            files.add(path)
    for dirname in INCLUDE_DIRS:
        root = Path(dirname)
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and not excluded(path.as_posix()):
                files.add(path)
    return sorted(files, key=lambda path: path.as_posix())


def missing_required(files: list[Path]) -> list[str]:
    included = {path.as_posix() for path in files}
    return [name for name in REQUIRED_FILES if name not in included]


def manifest_text(files: list[Path], archive_path: str) -> str:
    groups = [
        ("Source", ["src/", "prompts/", "tests/", "requirements.txt"]),
        ("Canonical data and cached API evidence", ["data/generated/", "data/runs/"]),
        ("Paper, tables, figures, and audits", ["paper/"]),
        ("Top-level summaries", ["README.md", "RESULTS_SUMMARY.md"]),
    ]
    group_rows = []
    for label, prefixes in groups:
        matched = [
            path
            for path in files
            if any(path.as_posix().startswith(prefix) or path.as_posix() == prefix for prefix in prefixes)
        ]
        group_rows.append(f"- {label}: {len(matched)} files")

    file_rows = "\n".join(f"- `{path.as_posix()}`" for path in files)
    excluded_rows = "\n".join(f"- `{pattern}`" for pattern in EXCLUDE_PATTERNS)
    required_missing = missing_required(files)
    missing_text = "none" if not required_missing else ", ".join(f"`{name}`" for name in required_missing)

    return "\n".join(
        [
            "# Supplement Package Manifest",
            "",
            "This generated manifest defines the files intended for an anonymized/release supplement.",
            "The companion zip is built deterministically from this file list with fixed archive timestamps.",
            "",
            "## Archive",
            "",
            f"- Default path: `{archive_path}`",
            f"- Included files: {len(files)}",
            f"- Missing required files: {missing_text}",
            "",
            "## Groups",
            "",
            "\n".join(group_rows),
            "",
            "## Exclusion Policy",
            "",
            "The package excludes API keys, local tool state, Python bytecode, LaTeX build intermediates, older smoke-run traces, and the zip file itself.",
            "",
            excluded_rows,
            "",
            "## Included Files",
            "",
            file_rows,
            "",
            "## Rebuild",
            "",
            "```bash",
            "conda run -n ask_dont_guess python src/make_supplement_package.py",
            "```",
            "",
        ]
    )


def write_zip(files: list[Path], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            info = zipfile.ZipInfo(path.as_posix(), date_time=FIXED_ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    out_path = Path(args.out)

    files = sorted(set(collect_files()) | {manifest_path}, key=lambda path: path.as_posix())
    write_text(manifest_path, manifest_text(files, out_path.as_posix()))
    files = collect_files()

    missing = missing_required(files)
    if missing:
        raise SystemExit(f"missing required supplement files: {', '.join(missing)}")

    if not args.manifest_only:
        write_zip(files, out_path)
        print(f"wrote supplement archive to {out_path}")
    print(f"wrote supplement manifest to {manifest_path}")
    print(f"included {len(files)} files")


if __name__ == "__main__":
    main()
