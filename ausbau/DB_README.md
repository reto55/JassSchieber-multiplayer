# Schieber Database Layer Refactoring

This directory contains the refactored database layer for the Schieber card game. The new implementation provides a more robust, object-oriented approach to database operations.

## Key Improvements

1. **Object-Oriented Design**
   - New `DatabaseManager` class encapsulates all database operations
   - Properly manages connections and resources
   - Supports context manager pattern (`with` statement)

2. **Improved Error Handling**
   - Better exception handling for database operations
   - Detailed error messages
   - Transaction support to ensure data integrity

3. **Schema Management**
   - Automated schema creation with proper constraints
   - Foreign key relationships to maintain data integrity
   - Clear separation of schema definition from data operations

4. **Clean API**
   - Well-documented methods with clear parameter definitions
   - Consistent return values
   - Logical organization of related functions

5. **Migration Support**
   - Tool to migrate data from old format to new format
   - Preserves existing data while upgrading schema
   - Safer data handling during migration

6. **Backward Compatibility**
   - Adapter layer to support existing code without major changes
   - Maintains same function signatures as the original code
   - Gradual transition path to the new API

## Key Files

- `database_manager.py` - Core implementation of the database layer
- `db_adapter.py` - Compatibility layer to support existing code
- `db_migration.py` - Tool to migrate data from old format to new
- `db_example.py` - Examples demonstrating how to use the new database layer

## How to Use

### New Code

For new code, use the `DatabaseManager` class directly:

```python
from database_manager import DatabaseManager

# Create a database manager
db = DatabaseManager("schieber.db")
db.connect()

# Create schema if needed
db.create_schema()

# Use the database manager's methods
game_id = db.create_schieber_game(end_sum=2500)
db.create_play_record(schieber_id=game_id, ...)

# Close the connection when done
db.close()
```

### With Context Manager

```python
from database_manager import DatabaseManager

# Use with statement to automatically handle connection
with DatabaseManager("schieber.db") as db:
    game_id = db.create_schieber_game(end_sum=2500)
    stats = db.get_game_stats(game_id)
    print(f"Game stats: {stats}")
```

### Existing Code Compatibility

For existing code, you can use the adapter functions:

```python
from db_adapter import create_connection, create_game, create_play

# Create connection (returns a DatabaseManager instance)
conn = create_connection("schieber.db")

# Use the old-style functions with the new backend
create_game(conn, game_data)
create_play(conn, play_data)
```

### Data Migration

To migrate data from an old database to the new format:

```python
from db_migration import migrate_database

# Migrate data from old database to new
migrate_database("old_schieber.db", "new_schieber.db")
```

## Implementation Notes

1. The new schema adds primary keys and foreign key constraints
2. Default player records (compo, compn, compe, comps) are created automatically
3. Timestamps are managed more cleanly
4. Error handling is more robust throughout the codebase

## Next Steps

1. Update the main game code to use the new database layer directly
2. Add more complex queries for game analysis
3. Create a proper data access layer for business logic
4. Add unit tests for database operations