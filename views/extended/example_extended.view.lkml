# Extended view — adds or overrides fields from a base view for a specific context.

view: +example_table {
  dimension: category {
    label: "Service Category"
  }

  dimension: is_high_value {
    type: yesno
    sql: ${TABLE}.value > 1000 ;;
    label: "High Value?"
    description: "True if value exceeds 1,000"
  }
}
