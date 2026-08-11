---
type: Python Method
title: fetch_all
resource: ausbau/database_manager.py#L113-L127
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/database_manager/DatabaseManager/execute_query
  called_by:
  - functions/ausbau/database_manager/DatabaseManager/create_schema
---

# Signature

`def fetch_all(self, query, params=None):`

# Calls

- [execute_query](../../../../functions/ausbau/database_manager/DatabaseManager/execute_query.md)

# Called by

- [create_schema](../../../../functions/ausbau/database_manager/DatabaseManager/create_schema.md)