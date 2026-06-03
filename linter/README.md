# ABUHB LookML Linter

Custom rule-based linter. Catches best-practice violations before they reach Looker.

## Install
```bash
pip install -r linter/requirements.txt
```

## Usage
```bash
python linter/lookml_linter.py                   # lint entire repo
python linter/lookml_linter.py views/base/        # lint a folder
python linter/lookml_linter.py --strict           # fail on warnings (CI)
python linter/lookml_linter.py --errors-only      # errors only
```

## Rules

| Rule | Severity | Check |
|------|----------|-------|
| `view_missing_primary_key` | 🔴 error | View has no `primary_key: yes` dimension |
| `derived_table_select_star` | 🔴 error | Derived table SQL uses `SELECT *` |
| `parse_error` | 🔴 error | File could not be parsed |
| `dimension_missing_label` | 🟡 warning | Dimension missing `label:` |
| `measure_missing_label` | 🟡 warning | Measure missing `label:` |
| `measure_missing_drill_fields` | 🟡 warning | Measure missing `drill_fields` |
| `dimension_group_missing_timeframes` | 🟡 warning | `dimension_group` missing `timeframes` |
| `explore_missing_label` | 🟡 warning | Explore missing `label:` |
| `sql_table_name_format` | 🟡 warning | `sql_table_name` not in backtick format |
| `dimension_missing_description` | 🔵 info | Dimension missing `description:` |
| `explore_missing_description` | 🔵 info | Explore missing `description:` |

## Adding Rules
Add checks inside `check_view()` or `check_model()` in `lookml_linter.py`.
Append a `LintIssue` with `rule`, `message`, `severity`, and `location`.

## CI (GitHub Actions)

Add `.github/workflows/lint.yml` to your repo:

```yaml
name: LookML Lint
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r linter/requirements.txt
      - run: python linter/lookml_linter.py --strict
```

> **Note:** Adding this file requires a token with `workflow` scope.
> Run `gh auth refresh -s workflow` then create the file manually or via CLI.
