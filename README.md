# LookML Template Repository

Best-practice LookML project structure for Looker development at ABUHB.

---

## Quick Start

1. Click **Use this template** → create your repo
2. Open in GitHub Codespaces — the devcontainer installs the `Looker.lkml` VS Code extension automatically
3. Install the pre-commit hook so the linter runs on every commit:
   ```bash
   pip install -r linter/requirements.txt
   pre-commit install
   ```
4. Replace the example files with your own views and models
5. Run LookML validation in the Looker IDE before every merge

---

## Folder Structure

```
.
├── .devcontainer/       # Codespaces config — LookML extension, Python linter
├── .pre-commit-config.yaml  # Runs the linter automatically on git commit
├── linter/              # Custom ABUHB LookML linter
│   ├── lookml_linter.py
│   ├── requirements.txt
│   └── README.md        # Linter rules and CI setup
├── models/              # LookML model files (.model.lkml)
├── views/
│   ├── base/            # Raw table views — one per BigQuery table
│   ├── derived/         # Derived tables (SQL or native DT)
│   └── extended/        # Views that extend base views
├── explores/            # Explore definitions (if split from models)
├── tests/               # LookML data tests
├── dashboards/          # LookML dashboards (.dashboard.lookml)
├── manifests/           # manifest.lkml — project-level config
└── docs/                # Extended documentation
```

---

## Linter & Pre-commit Hook

This repo includes a custom LookML linter at `linter/lookml_linter.py`. It is wired as a **pre-commit hook** — it runs automatically whenever you `git commit` a `.lkml` file and blocks the commit if violations are found.

**Setup (one-time per developer):**
```bash
pip install -r linter/requirements.txt
pre-commit install
```

**Run manually:**
```bash
python linter/lookml_linter.py               # lint entire repo
python linter/lookml_linter.py views/base/   # lint a folder
pre-commit run lookml-lint --all-files       # via pre-commit
```

See [`linter/README.md`](linter/README.md) for the full rule list and CI setup.

---

## File Types

### Models (`.model.lkml`)

The entry point for a Looker connection. Defines which views are exposed and how they join.

- One model per business domain (e.g. `finance.model.lkml`, `workforce.model.lkml`)
- Always set `label:` so business users see friendly names
- Keep explore definitions in models unless complexity warrants splitting

```lookml
connection: "bigquery_connection"

include: "/views/**/*.view.lkml"

explore: patient_activity {
  label: "Patient Activity"
  description: "Explore for patient activity data"
  join: ward_dim {
    type: left_outer
    sql_on: ${patient_activity.ward_id} = ${ward_dim.ward_id} ;;
    relationship: many_to_one
  }
}
```

---

### Views (`.view.lkml`)

A view maps to a table or derived table. Contains all dimension and measure definitions.

- **Base views** (`views/base/`): one per BigQuery table, named to match the table
- **Derived table views** (`views/derived/`): complex SQL or native DT logic
- **Extended views** (`views/extended/`): add/override fields for a specific explore context

```lookml
view: patient_activity {
  sql_table_name: `project.dataset.patient_activity` ;;

  dimension: patient_id {
    type: string
    primary_key: yes
    sql: ${TABLE}.patient_id ;;
    label: "Patient ID"
    description: "Unique identifier for the patient"
  }

  dimension_group: activity_date {
    type: time
    timeframes: [date, week, month, quarter, year]
    sql: ${TABLE}.activity_date ;;
    label: "Activity Date"
  }

  measure: count {
    type: count
    label: "Count of Records"
    drill_fields: [patient_id, activity_date_date]
  }
}
```

---

### Derived Tables

**SQL Derived Table:**
```lookml
view: monthly_admissions {
  derived_table: {
    sql:
      SELECT
        DATE_TRUNC(admission_date, MONTH) AS admission_month,
        ward_id,
        COUNT(*) AS admission_count
      FROM `project.dataset.admissions`
      GROUP BY 1, 2
    ;;
    persist_for: "24 hours"
  }
}
```

**Native Derived Table (NDT):**
```lookml
view: ward_summary {
  derived_table: {
    explore_source: patient_activity {
      column: ward_id {}
      column: total_count { field: patient_activity.count }
      filters: [patient_activity.activity_date_year: "last 1 year"]
    }
  }
}
```

---

### Dimensions

| Type | Use when |
|------|----------|
| `string` | Text identifiers, categories |
| `number` | Numeric fields used in calculations |
| `yesno` | Boolean flags |
| `dimension_group` | Any date or timestamp |
| `tier` | Bucketing a numeric field |

Always set `label:` and `description:` — this is what users see.

---

### Measures

| Type | Use when |
|------|----------|
| `count` | Row count |
| `count_distinct` | Unique values |
| `sum` | Summing a numeric field |
| `average` | Mean of a numeric field |
| `max` / `min` | Extremes |

Always set `drill_fields` on key measures.

---

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| View file | `snake_case` matching table name | `patient_activity.view.lkml` |
| Model file | `domain_name.model.lkml` | `clinical.model.lkml` |
| Dimension | `snake_case` | `ward_id` |
| Measure | Prefix with outcome | `total_admissions`, `count_patients` |
| Derived table | Suffix with `_dt` | `ward_summary_dt` |
| Explore | Noun phrase, user-readable | `patient_activity` |

---

## Best Practices

1. **Never use `SELECT *`** in derived tables — always name columns explicitly
2. **Set `primary_key: yes`** on the unique identifier of every view
3. **Use `${TABLE}.field`** syntax — never hardcode table names in SQL
4. **One file per view** — do not stack multiple view definitions in one file
5. **Keep business logic in LookML** — use `always_filter` and `conditionally_filter`
6. **Comment complex SQL** — future you will thank present you
7. **Add data tests** — at least one test per critical measure
8. **Use `tags`** to mark views/explores by workstream (e.g. `["finance", "reporting"]`)
9. **Persist derived tables appropriately** — use `persist_for` or `sql_trigger_value`
10. **Review query cost before publishing** — use BigQuery Query Validator in Looker admin

---

## LookML Data Tests

```lookml
test: patient_id_is_unique {
  explore_source: patient_activity {
    column: patient_id {}
  }
  assert: patient_id {
    is_not_null: yes
  }
}
```

Run via the Looker IDE or `pre-commit run lookml-lint --all-files`.
