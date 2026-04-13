# Migration Guide: Imports and Utilities

This guide provides steps to migrate your code from the old imports structure to the new modular utilities.

## Step 1: Update Your Imports

### Before

```python
from imports import *
from time import sleep
from Cards import *
```

### After

**Option 1 (Gradual Transition)**
```python
from imports_new import *  # Maintains backward compatibility
```

**Option 2 (Recommended)**
```python
# Explicitly import only what you need
from utils.db_utils import create_connection, create_game
from utils.card_utils import sort_trumpf, farbe_lang
from utils.game_utils import dauergame, max_game
from Cards import Schieber, weis, spieler_id
from time import sleep
```

## Step 2: Update Database Access

### Before

```python
conn = create_connection("schieber.db")
with conn:
    create_game(conn, game_data)
    create_play(conn, play_data)
```

### After

```python
from utils.db_utils import create_connection, create_game, create_play

conn = create_connection("schieber.db")
with conn:
    create_game(conn, game_data)
    create_play(conn, play_data)
```

## Step 3: Update Card Utilities

### Before

```python
sorted_cards = sort_trumpf(player, "Eicheln")
```

### After

```python
from utils.card_utils import sort_trumpf

sorted_cards = sort_trumpf(player, "Eicheln")
```

## Step 4: Update Game Utilities

### Before

```python
hours, minutes, seconds = dauergame(game)
max_card = max_game(dealer, operator, first, game)
```

### After

```python
from utils.game_utils import dauergame, max_game

hours, minutes, seconds = dauergame(game)
max_card = max_game(dealer, operator, first, game)
```

## Step 5: Use New Utility Functions

The refactoring also adds new utility functions that weren't available before:

```python
from utils.game_utils import format_game_duration, check_game_end, get_winner

# Format game duration as a string
duration_str = format_game_duration(game)
print(f"Game duration: {duration_str}")

# Check if the game is over
if check_game_end(pointSN, pointOW, end_game):
    winner = get_winner(pointSN, pointOW)
    print(f"Game over! Winner: {winner}")
```

## Step 6: Replace Global Variables

Instead of relying on global variables, import them explicitly:

### Before

```python
global Schieber, weis, spieler_id
# Use variables directly
```

### After

```python
from Cards import Schieber, weis, spieler_id
# Use the imported variables
```

## Example: Complete File Migration

### Before

```python
# -*- coding: UTF-8 -*-
from imports import *
from time import sleep

def my_function():
    conn = create_connection("schieber.db")
    with conn:
        dealer = Play(1)
        sorted_cards = sort_trumpf(dealer.compo, "Eicheln")
        create_game(conn, game_data)
        hours, minutes, seconds = dauergame(Schieber)
        print(f"Game took {hours}h {minutes}m {seconds}s")
```

### After

```python
# -*- coding: UTF-8 -*-
from utils.db_utils import create_connection, create_game
from utils.card_utils import sort_trumpf
from utils.game_utils import dauergame, format_game_duration
from Cards import Play, Schieber
from time import sleep

def my_function():
    conn = create_connection("schieber.db")
    with conn:
        dealer = Play(1)
        sorted_cards = sort_trumpf(dealer.compo, "Eicheln")
        create_game(conn, game_data)
        # Using the new utility function
        duration_str = format_game_duration(Schieber)
        print(f"Game took {duration_str}")
```

## Testing Your Migration

After migrating, test your code thoroughly to ensure it still works correctly. Pay special attention to:

1. Database interactions
2. Card sorting and manipulation
3. Game mechanics involving the utility functions

## Getting Help

If you encounter issues during migration, check:
- The docstrings in the utility modules
- The example code in this guide
- The IMPORTS_README.md file for more context