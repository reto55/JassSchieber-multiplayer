---
type: Python Method
title: create_stich_record
resource: ausbau/database_manager.py#L381-L408
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/database_manager/DatabaseManager/execute_query
  called_by:
  - functions/ausbau/db_adapter/create_stich
  - functions/ausbau/db_migration/migrate_database
---

# Signature

`def create_stich_record(self, schieber_id, runde, spiel, zug, spieler_id, stich):`

# Calls

- [execute_query](../../../../functions/ausbau/database_manager/DatabaseManager/execute_query.md)

# Called by

- [create_stich](../../../../functions/ausbau/db_adapter/create_stich.md)
- [migrate_database](../../../../functions/ausbau/db_migration/migrate_database.md)