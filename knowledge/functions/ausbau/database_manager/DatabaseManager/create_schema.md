---
type: Python Method
title: create_schema
resource: ausbau/database_manager.py#L145-L269
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/database_manager/DatabaseManager/fetch_all
  - functions/ausbau/database_manager/DatabaseManager/execute_query
  called_by:
  - functions/ausbau/db_example/demonstrate_basic_operations
  - functions/ausbau/db_migration/migrate_database
---

# Signature

`def create_schema(self):`

# Calls

- [fetch_all](../../../../functions/ausbau/database_manager/DatabaseManager/fetch_all.md)
- [execute_query](../../../../functions/ausbau/database_manager/DatabaseManager/execute_query.md)

# Called by

- [demonstrate_basic_operations](../../../../functions/ausbau/db_example/demonstrate_basic_operations.md)
- [migrate_database](../../../../functions/ausbau/db_migration/migrate_database.md)