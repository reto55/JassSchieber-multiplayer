---
type: Python Function
title: migrate_database
resource: ausbau/db_migration.py#L11-L155
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/database_manager/DatabaseManager/create_schema
  - functions/ausbau/database_manager/DatabaseManager/execute_query
  - functions/ausbau/database_manager/DatabaseManager/create_game_record
  - functions/ausbau/database_manager/DatabaseManager/create_play_record
  - functions/ausbau/database_manager/DatabaseManager/create_wys_record
  - functions/ausbau/database_manager/DatabaseManager/create_wwys_record
  - functions/ausbau/database_manager/DatabaseManager/create_stich_record
---

# Signature

`def migrate_database(old_db_path, new_db_path=None):`

# Calls

- [create_schema](../../../functions/ausbau/database_manager/DatabaseManager/create_schema.md)
- [execute_query](../../../functions/ausbau/database_manager/DatabaseManager/execute_query.md)
- [create_game_record](../../../functions/ausbau/database_manager/DatabaseManager/create_game_record.md)
- [create_play_record](../../../functions/ausbau/database_manager/DatabaseManager/create_play_record.md)
- [create_wys_record](../../../functions/ausbau/database_manager/DatabaseManager/create_wys_record.md)
- [create_wwys_record](../../../functions/ausbau/database_manager/DatabaseManager/create_wwys_record.md)
- [create_stich_record](../../../functions/ausbau/database_manager/DatabaseManager/create_stich_record.md)