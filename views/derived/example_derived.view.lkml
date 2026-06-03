# Derived table view — pre-aggregated or complex SQL logic.

view: example_derived {
  derived_table: {
    sql:
      SELECT
        DATE_TRUNC(created_at, MONTH)  AS month,
        category,
        COUNT(*)                        AS record_count,
        SUM(value)                      AS total_value
      FROM `your_project.your_dataset.example_table`
      WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 24 MONTH)
      GROUP BY 1, 2
    ;;
    persist_for: "24 hours"
  }

  dimension_group: month {
    type: time
    timeframes: [month, quarter, year]
    sql: ${TABLE}.month ;;
    label: "Month"
  }

  dimension: category {
    type: string
    sql: ${TABLE}.category ;;
    label: "Category"
  }

  measure: total_records {
    type: sum
    sql: ${TABLE}.record_count ;;
    label: "Total Records"
  }

  measure: total_value {
    type: sum
    sql: ${TABLE}.total_value ;;
    label: "Total Value"
    value_format_name: decimal_2
  }
}
