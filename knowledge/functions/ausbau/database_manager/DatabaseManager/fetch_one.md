---
type: Python Method
title: fetch_one
resource: ausbau/database_manager.py#L129-L143
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/database_manager/DatabaseManager/execute_query
  called_by:
  - functions/ausbau/database_manager/DatabaseManager/get_player_by_id
  - functions/ausbau/database_manager/DatabaseManager/get_spieler_id_by_name
  - functions/ausbau/database_manager/DatabaseManager/get_game_stats
  - functions/ausbau/database_manager/DatabaseManager/get_last_game_id
  - functions/ausbau/db_example/demonstrate_context_manager
---

# Signature

`def fetch_one(self, query, params=None):`

# Calls

- [execute_query](../../../../functions/ausbau/database_manager/DatabaseManager/execute_query.md)

# Called by

- [get_player_by_id](../../../../functions/ausbau/database_manager/DatabaseManager/get_player_by_id.md)
- [get_spieler_id_by_name](../../../../functions/ausbau/database_manager/DatabaseManager/get_spieler_id_by_name.md)
- [get_game_stats](../../../../functions/ausbau/database_manager/DatabaseManager/get_game_stats.md)
- [get_last_game_id](../../../../functions/ausbau/database_manager/DatabaseManager/get_last_game_id.md)
- [demonstrate_context_manager](../../../../functions/ausbau/db_example/demonstrate_context_manager.md)