#!/usr/bin/env python3
"""Pre-push checks for the India weather project.

Run from anywhere:   python scripts/check_before_push.py
Exits with code 1 if something that would break the GitHub page is found.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = [
    "README.md", "LICENSE", "requirements.txt", ".gitignore",
    "app.py", "prepare_data.py",
    "notebooks/01_data_collection_and_cleaning.ipynb",
    "notebooks/02_exploratory_data_analysis.ipynb",
    "notebooks/03_forecasting_models.ipynb",
    "data/monthly_temperature.csv",
    "reports/forecast_next_12_months.csv",
    "reports/metrics_backtest_by_city.csv",
    "reports/metrics_test_2026_by_city.csv",
    "reports/metrics_test_2026_overall.csv",
    "reports/best_model_per_city.csv",
    "reports/figures/dashboard.png",
]
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".ipynb_checkpoints"}
IGNORED_PREFIXES = ("data/raw/", "data/processed/")   # git-ignored, so never pushed

errors, warnings = [], []


def exists_exact_case(rel):
    """True only if the path exists with exactly this capitalisation (GitHub is case-sensitive)."""
    cur = ROOT
    for part in Path(rel).parts:
        if not cur.is_dir() or part not in {p.name for p in cur.iterdir()}:
            return False
        cur = cur / part
    return True


# 1. required files
for rel in REQUIRED:
    if not exists_exact_case(rel):
        errors.append(f"Missing file: {rel}")

# 2. README images and relative links
readme = ROOT / "README.md"
if readme.exists():
    text = readme.read_text(encoding="utf-8")
    links = re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text)
    links += re.findall(r'<img[^>]+src="([^"]+)"', text)
    links += re.findall(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)", text)
    seen = set()
    for link in links:
        link = link.split("#")[0]
        if not link or link in seen or link.startswith(("http://", "https://", "mailto:")):
            continue
        seen.add(link)
        if not exists_exact_case(link):
            errors.append(f"README link is broken (check spelling and capital letters): {link}")
    n_img = len([l for l in set(links) if l.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg"))])
    print(f"[info] README references {n_img} images")
    for marker in ("add your Streamlit link here", "YOUR-USERNAME", "YOUR-APP-URL"):
        if marker in text:
            warnings.append(f"README still contains a placeholder: '{marker}'")

# 3. LICENSE placeholder
lic = ROOT / "LICENSE"
if lic.exists() and "YOUR NAME" in lic.read_text(encoding="utf-8"):
    warnings.append("LICENSE still says 'YOUR NAME'")

# 4. notebooks should contain outputs (charts) so GitHub shows results
for nb_path in sorted((ROOT / "notebooks").glob("*.ipynb")):
    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        n_out = sum(1 for c in nb.get("cells", []) if c.get("cell_type") == "code" and c.get("outputs"))
        if n_out == 0:
            warnings.append(f"{nb_path.name} has no saved outputs. Run all cells and save, so charts show on GitHub")
    except Exception as e:
        errors.append(f"Could not read {nb_path.name}: {e}")

# 5. big files that would be pushed
for p in ROOT.rglob("*"):
    if not p.is_file() or any(part in SKIP_DIRS for part in p.parts):
        continue
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith(IGNORED_PREFIXES) or p.name == "india_weather_daily.csv":
        continue
    size_mb = p.stat().st_size / 1e6
    if size_mb > 50:
        errors.append(f"File too large for a normal push ({size_mb:.0f} MB): {rel}")
    elif size_mb > 25:
        warnings.append(f"Large file ({size_mb:.0f} MB): {rel}")

for e in errors:
    print(f"[ERROR] {e}")
for w in warnings:
    print(f"[WARN]  {w}")
if not errors and not warnings:
    print("[OK] All checks passed. Ready to push.")
elif not errors:
    print("\n[OK] No blocking problems. Review the warnings above, then push.")
else:
    print(f"\n{len(errors)} problem(s) must be fixed before pushing.")
    sys.exit(1)
