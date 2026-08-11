---
type: Python Method
title: create_wys_record
resource: ausbau/database_manager.py#L410-L437
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/database_manager/DatabaseManager/execute_query
  called_by:
  - functions/ausbau/db_adapter/create_wys
  - functions/ausbau/db_migration/migrate_database
---

# Signature

`def create_wys_record(self, schieber_id, runde, spiel, spieler_id, first, wys):`

# Calls

- [execute_query](../../../../functions/ausbau/database_manager/DatabaseManager/execute_query.md)

# Called by

- [create_wys](../../../../functions/ausbau/db_adapter/create_wys.md)
- [migrate_database](../../../../functions/ausbau/db_migration/migrate_database.md)