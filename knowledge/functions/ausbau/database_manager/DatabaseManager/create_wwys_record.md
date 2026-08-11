---
type: Python Method
title: create_wwys_record
resource: ausbau/database_manager.py#L439-L466
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/database_manager/DatabaseManager/execute_query
  called_by:
  - functions/ausbau/db_adapter/create_wwys
  - functions/ausbau/db_migration/migrate_database
---

# Signature

`def create_wwys_record(self, schieber_id, runde, spiel, spieler_id, first, wwys):`

# Calls

- [execute_query](../../../../functions/ausbau/database_manager/DatabaseManager/execute_query.md)

# Called by

- [create_wwys](../../../../functions/ausbau/db_adapter/create_wwys.md)
- [migrate_database](../../../../functions/ausbau/db_migration/migrate_database.md)