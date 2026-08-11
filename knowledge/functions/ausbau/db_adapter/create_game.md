---
type: Python Function
title: create_game
resource: ausbau/db_adapter.py#L44-L66
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/db_adapter/get_db_manager
  - functions/ausbau/database_manager/DatabaseManager/create_game_record
---

# Signature

`def create_game(conn, game):`

# Calls

- [get_db_manager](../../../functions/ausbau/db_adapter/get_db_manager.md)
- [create_game_record](../../../functions/ausbau/database_manager/DatabaseManager/create_game_record.md)