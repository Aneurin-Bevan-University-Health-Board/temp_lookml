# Base view — one per BigQuery table. File name should match the table name.

view: example_table {
  sql_table_name: `your_project.your_dataset.example_table` ;;

  dimension: id {
    type: string
    primary_key: yes
    sql: ${TABLE}.id ;;
    label: "ID"
    description: "Unique row identifier"
  }

  dimension: category {
    type: string
    sql: ${TABLE}.category ;;
    label: "Category"
  }

  dimension_group: created {
    type: time
    timeframes: [date, week, month, quarter, year]
    sql: ${TABLE}.created_at ;;
    label: "Created"
  }

  dimension: value {
    type: number
    sql: ${TABLE}.value ;;
    label: "Value"
    hidden: yes
  }

  measure: count {
    type: count
    label: "Count"
    drill_fields: [id, category, created_date]
  }

  measure: total_value {
    type: sum
    sql: ${value} ;;
    label: "Total Value"
    value_format_name: decimal_2
  }

  measure: average_value {
    type: average
    sql: ${value} ;;
    label: "Average Value"
    value_format_name: decimal_2
  }
}
