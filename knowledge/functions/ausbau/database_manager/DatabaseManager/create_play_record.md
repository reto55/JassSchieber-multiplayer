---
type: Python Method
title: create_play_record
resource: ausbau/database_manager.py#L341-L379
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/database_manager/DatabaseManager/execute_query
  called_by:
  - functions/ausbau/db_adapter/create_play
  - functions/ausbau/db_example/demonstrate_basic_operations
  - functions/ausbau/db_example/demonstrate_transaction
  - functions/ausbau/db_migration/migrate_database
---

# Signature

`def create_play_record(self, schieber_id, runde, spiel, zug, spieler_id, first, operator, realname, pointOW, pointSN, eicheln, rosen, schellen, schilten):`

# Calls

- [execute_query](../../../../functions/ausbau/database_manager/DatabaseManager/execute_query.md)

# Called by

- [create_play](../../../../functions/ausbau/db_adapter/create_play.md)
- [demonstrate_basic_operations](../../../../functions/ausbau/db_example/demonstrate_basic_operations.md)
- [demonstrate_transaction](../../../../functions/ausbau/db_example/demonstrate_transaction.md)
- [migrate_database](../../../../functions/ausbau/db_migration/migrate_database.md)