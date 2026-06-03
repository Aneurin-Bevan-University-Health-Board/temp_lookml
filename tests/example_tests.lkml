# LookML data tests — validate model assumptions.
# Run via Looker IDE: Content > LookML > Run Tests

test: example_id_not_null {
  explore_source: example_explore {
    column: id {}
  }
  assert: id {
    is_not_null: yes
  }
}
