---
type: Python Method
title: create_game_record
resource: ausbau/database_manager.py#L310-L339
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/database_manager/DatabaseManager/execute_query
  called_by:
  - functions/ausbau/db_adapter/create_game
  - functions/ausbau/db_migration/migrate_database
---

# Signature

`def create_game_record(self, schieber_id, runde, spiel, zug, spieler_id, first, operator, karte):`

# Calls

- [execute_query](../../../../functions/ausbau/database_manager/DatabaseManager/execute_query.md)

# Called by

- [create_game](../../../../functions/ausbau/db_adapter/create_game.md)
- [migrate_database](../../../../functions/ausbau/db_migration/migrate_database.md)