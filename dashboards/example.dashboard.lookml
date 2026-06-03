- dashboard: example_dashboard
  title: "Example Dashboard"
  layout: newspaper
  preferred_viewer: dashboards-next

  elements:

  - title: "Record Count by Month"
    name: record_count_by_month
    model: example
    explore: example_explore
    type: looker_column
    fields: [example_table.created_month, example_table.count]
    sorts: [example_table.created_month asc]
    limit: 24
    col: 0
    row: 0
    width: 12
    height: 6
