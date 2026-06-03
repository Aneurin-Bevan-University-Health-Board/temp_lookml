#!/usr/bin/env python3
"""
ABUHB Custom LookML Linter.

Usage:
    python linter/lookml_linter.py                  # lint entire repo
    python linter/lookml_linter.py views/base/       # lint a folder
    python linter/lookml_linter.py --strict          # fail on warnings (CI)
    python linter/lookml_linter.py --errors-only     # suppress warnings/info
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Literal

import lkml
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
Severity = Literal["error", "warning", "info"]


@dataclass
class LintIssue:
    file: str
    rule: str
    message: str
    severity: Severity = "error"
    location: str = ""


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

def check_view(view: dict, filename: str) -> list[LintIssue]:
    issues: list[LintIssue] = []
    name = view.get("name", "<unknown>")
    loc = f"view: {name}"
    dims = view.get("dimensions", [])
    measures = view.get("measures", [])

    # ERROR: no primary_key dimension
    if dims and not any(d.get("primary_key") == "yes" for d in dims):
        issues.append(LintIssue(filename, "view_missing_primary_key",
            "No dimension with primary_key: yes", "error", loc))

    # ERROR: SELECT * in derived table SQL
    dt = view.get("derived_table")
    if dt and isinstance(dt, dict):
        sql = dt.get("sql", "")
        if "SELECT *" in sql.upper().replace("\n", " "):
            issues.append(LintIssue(filename, "derived_table_select_star",
                "Derived table uses SELECT * — name columns explicitly",
                "error", f"{loc} > derived_table"))

    # WARNING: sql_table_name not in backtick format
    sql_table = view.get("sql_table_name", "")
    if sql_table and not sql_table.strip().startswith("`"):
        issues.append(LintIssue(filename, "sql_table_name_format",
            "sql_table_name should use backtick format: `project.dataset.table`",
            "warning", loc))

    # WARNING: dimension missing label
    for d in dims:
        if not d.get("label"):
            issues.append(LintIssue(filename, "dimension_missing_label",
                "Missing label:", "warning",
                f"{loc} > dimension: {d.get('name', '?')}"))

    # WARNING: measure missing label
    for m in measures:
        if not m.get("label"):
            issues.append(LintIssue(filename, "measure_missing_label",
                "Missing label:", "warning",
                f"{loc} > measure: {m.get('name', '?')}"))

    # WARNING: measure missing drill_fields
    for m in measures:
        if not m.get("drill_fields"):
            issues.append(LintIssue(filename, "measure_missing_drill_fields",
                "Missing drill_fields", "warning",
                f"{loc} > measure: {m.get('name', '?')}"))

    # WARNING: dimension_group missing timeframes
    for dg in view.get("dimension_groups", []):
        if not dg.get("timeframes"):
            issues.append(LintIssue(filename, "dimension_group_missing_timeframes",
                "dimension_group has no timeframes — add [date, week, month, quarter, year]",
                "warning", f"{loc} > dimension_group: {dg.get('name', '?')}"))

    # INFO: dimension missing description
    for d in dims:
        if not d.get("description"):
            issues.append(LintIssue(filename, "dimension_missing_description",
                "Missing description:", "info",
                f"{loc} > dimension: {d.get('name', '?')}"))

    return issues


def check_model(parsed: dict, filename: str) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for ex in parsed.get("explores", []):
        name = ex.get("name", "<unknown>")
        loc = f"explore: {name}"
        if not ex.get("label"):
            issues.append(LintIssue(filename, "explore_missing_label",
                "Missing label:", "warning", loc))
        if not ex.get("description"):
            issues.append(LintIssue(filename, "explore_missing_description",
                "Missing description:", "info", loc))
    return issues


def lint_file(path: Path) -> list[LintIssue]:
    try:
        parsed = lkml.load(path.read_text())
    except Exception as e:
        return [LintIssue(str(path), "parse_error", f"Failed to parse: {e}", "error")]
    issues = []
    for view in parsed.get("views", []):
        issues.extend(check_view(view, str(path)))
    if parsed.get("explores"):
        issues.extend(check_model(parsed, str(path)))
    return issues


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

COLOUR = {"error": "red", "warning": "yellow", "info": "cyan"}
ICON   = {"error": "✖", "warning": "⚠", "info": "ℹ"}


def render(issues: list[LintIssue], n_files: int) -> None:
    if not issues:
        console.print(f"\n[green]✔ No issues in {n_files} file(s).[/green]\n")
        return
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    t.add_column("Sev", width=3)
    t.add_column("File", style="dim")
    t.add_column("Location")
    t.add_column("Rule", style="bold")
    t.add_column("Message")
    for i in sorted(issues, key=lambda x: (x.severity != "error", x.severity != "warning", x.file)):
        c = COLOUR[i.severity]
        t.add_row(f"[{c}]{ICON[i.severity]}[/{c}]", i.file, i.location, i.rule, i.message)
    console.print(t)
    e = sum(1 for i in issues if i.severity == "error")
    w = sum(1 for i in issues if i.severity == "warning")
    n = sum(1 for i in issues if i.severity == "info")
    console.print(f"Files: {n_files}  [red]Errors: {e}[/red]  [yellow]Warnings: {w}[/yellow]  [cyan]Info: {n}[/cyan]\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="ABUHB LookML Linter")
    p.add_argument("path", nargs="?", default=".", help="File or directory to lint")
    p.add_argument("--strict", action="store_true", help="Exit 1 on warnings too")
    p.add_argument("--errors-only", action="store_true", help="Only show errors")
    args = p.parse_args()

    root = Path(args.path)
    files = [root] if root.is_file() else sorted(root.rglob("*.lkml"))
    if not files:
        console.print("[yellow]No .lkml files found.[/yellow]")
        sys.exit(0)

    console.print(f"\n[bold]ABUHB LookML Linter[/bold] — {len(files)} file(s)\n")
    all_issues: list[LintIssue] = []
    for f in files:
        all_issues.extend(lint_file(f))
    if args.errors_only:
        all_issues = [i for i in all_issues if i.severity == "error"]

    render(all_issues, len(files))

    if any(i.severity == "error" for i in all_issues):
        sys.exit(1)
    if args.strict and any(i.severity == "warning" for i in all_issues):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
