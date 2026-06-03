# Example model — rename to match your business domain (e.g. clinical.model.lkml)

connection: "your_bigquery_connection"

include: "/views/base/*.view.lkml"
include: "/views/derived/*.view.lkml"
include: "/views/extended/*.view.lkml"

explore: example_explore {
  label: "Example Explore"
  description: "Replace with your subject area description"

  # Prevent full-table scans
  # always_filter: {
  #   filters: [example_view.date_field: "last 90 days"]
  # }

  # Example join
  # join: dimension_table {
  #   type: left_outer
  #   sql_on: ${example_explore.dim_id} = ${dimension_table.dim_id} ;;
  #   relationship: many_to_one
  # }
}
