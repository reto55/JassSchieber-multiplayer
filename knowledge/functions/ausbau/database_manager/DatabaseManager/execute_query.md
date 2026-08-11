---
type: Python Method
title: execute_query
resource: ausbau/database_manager.py#L56-L84
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/database_manager/DatabaseManager/fetch_all
  - functions/ausbau/database_manager/DatabaseManager/fetch_one
  - functions/ausbau/database_manager/DatabaseManager/create_schema
  - functions/ausbau/database_manager/DatabaseManager/create_schieber_game
  - functions/ausbau/database_manager/DatabaseManager/update_schieber_game_end
  - functions/ausbau/database_manager/DatabaseManager/create_game_record
  - functions/ausbau/database_manager/DatabaseManager/create_play_record
  - functions/ausbau/database_manager/DatabaseManager/create_stich_record
  - functions/ausbau/database_manager/DatabaseManager/create_wys_record
  - functions/ausbau/database_manager/DatabaseManager/create_wwys_record
  - functions/ausbau/db_adapter/create_schieber
  - functions/ausbau/db_adapter/create_spieler
  - functions/ausbau/db_adapter/update_schieber
  - functions/ausbau/db_example/demonstrate_basic_operations
  - functions/ausbau/db_migration/migrate_database
---

# Signature

`def execute_query(self, query, params=None, commit=False):`

# Called by

- [fetch_all](../../../../functions/ausbau/database_manager/DatabaseManager/fetch_all.md)
- [fetch_one](../../../../functions/ausbau/database_manager/DatabaseManager/fetch_one.md)
- [create_schema](../../../../functions/ausbau/database_manager/DatabaseManager/create_schema.md)
- [create_schieber_game](../../../../functions/ausbau/database_manager/DatabaseManager/create_schieber_game.md)
- [update_schieber_game_end](../../../../functions/ausbau/database_manager/DatabaseManager/update_schieber_game_end.md)
- [create_game_record](../../../../functions/ausbau/database_manager/DatabaseManager/create_game_record.md)
- [create_play_record](../../../../functions/ausbau/database_manager/DatabaseManager/create_play_record.md)
- [create_stich_record](../../../../functions/ausbau/database_manager/DatabaseManager/create_stich_record.md)
- [create_wys_record](../../../../functions/ausbau/database_manager/DatabaseManager/create_wys_record.md)
- [create_wwys_record](../../../../functions/ausbau/database_manager/DatabaseManager/create_wwys_record.md)
- [create_schieber](../../../../functions/ausbau/db_adapter/create_schieber.md)
- [create_spieler](../../../../functions/ausbau/db_adapter/create_spieler.md)
- [update_schieber](../../../../functions/ausbau/db_adapter/update_schieber.md)
- [demonstrate_basic_operations](../../../../functions/ausbau/db_example/demonstrate_basic_operations.md)
- [migrate_database](../../../../functions/ausbau/db_migration/migrate_database.md)