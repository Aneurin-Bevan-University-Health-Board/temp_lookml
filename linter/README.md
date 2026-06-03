# ABUHB LookML Linter

Custom rule-based linter. Catches best-practice violations before they reach Looker.
Runs automatically on every `git commit` via pre-commit.

---

## Setup (one-time per developer)

```bash
pip install -r linter/requirements.txt
pre-commit install
```

That's it. The linter now runs automatically whenever you `git commit` any `.lkml` file.

---

## Pre-commit behaviour

- Triggers only when `.lkml` files are staged
- Blocks the commit if any **errors** are found
- With `--strict` (default): also blocks on **warnings**
- To bypass in an emergency: `git commit --no-verify` (use sparingly)

### Run manually

```bash
# Lint all .lkml files right now
pre-commit run lookml-lint --all-files

# Or run the script directly
python linter/lookml_linter.py
python linter/lookml_linter.py views/base/        # specific folder
python linter/lookml_linter.py --errors-only      # suppress warnings/info
```

### Loosen strictness during onboarding

If `--strict` is too noisy when first adopting this on an existing repo, edit `.pre-commit-config.yaml` and remove the `--strict` arg. Re-add it once warnings are resolved.

---

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

---

## Adding Rules

Add checks inside `check_view()` or `check_model()` in `lookml_linter.py`.
Append a `LintIssue` with `rule`, `message`, `severity`, and `location`.

---

## CI (GitHub Actions)

To also run the linter on PRs, add `.github/workflows/lint.yml`:

```yaml
name: LookML Lint
on:
  pull_request:
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

> Requires a token with `workflow` scope: `gh auth refresh -s workflow`
