# Imports and Utilities Refactoring

This document explains the improvements made to the imports and utilities in the Schieber card game.

## Key Improvements

1. **Modular Structure**
   - Split utilities into logical modules:
     - `db_utils.py`: Database access and operations
     - `card_utils.py`: Card manipulation and sorting
     - `game_utils.py`: Game mechanics and calculations
   - Created a proper `utils` package with `__init__.py`

2. **Explicit Imports**
   - Replaced wildcard imports (`from X import *`) with explicit imports
   - Reduced risk of namespace conflicts
   - Made dependencies clearer and more maintainable

3. **Better Documentation**
   - Added docstrings to explain function purposes
   - Included parameter and return value descriptions
   - Added module docstrings for context

4. **Improved Organization**
   - Grouped related functions together
   - Separated database code from game logic
   - Created a clearer structure for future development

5. **Backward Compatibility**
   - Provided `imports_new.py` alongside the original for gradual transition
   - Maintained wildcard imports for legacy code support

## How to Use the New Imports

### New Code

For new code, use the modular imports:

```python
# Import specific utilities
from utils.db_utils import create_connection, create_game
from utils.card_utils import sort_trumpf, farbe_lang
from utils.game_utils import calculate_points, get_winner

# Or use the centralized imports file
from imports_new import (
    create_connection, sort_trumpf, calculate_points,
    Schieber, weis, spieler_id
)
```

### Transitioning Existing Code

To transition existing code, replace:

```python
from imports import *
```

With:

```python
from imports_new import *
```

Or for better practice, use explicit imports:

```python
from imports_new import create_connection, create_game, sort_trumpf
```

## Next Steps

1. Update the main game files to use the new import structure
2. Remove legacy wildcard imports after transition
3. Add unit tests for utility functions
4. Further improve organization of game constants

## Directory Structure

```
/Schieber/
├── utils/
│   ├── __init__.py
│   ├── db_utils.py
│   ├── card_utils.py
│   └── game_utils.py
├── imports.py (original)
├── imports_new.py (refactored)
└── ... (other files)
```