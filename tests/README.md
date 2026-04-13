# Schieber Card Game Tests

This directory contains the test suite for the Schieber card game.

## Test Structure

The test suite is organized into the following files:

- `test_db_utils.py`: Tests for database utilities
- `test_card_utils.py`: Tests for card manipulation utilities
- `test_game_utils.py`: Tests for game mechanics utilities
- `test_integration.py`: Integration tests that verify interactions between modules

## Running Tests

You can run all tests using the following command from the project root directory:

```bash
python run_tests.py
```

Or you can run individual test files:

```bash
python -m unittest tests/test_db_utils.py
python -m unittest tests/test_card_utils.py
python -m unittest tests/test_game_utils.py
python -m unittest tests/test_integration.py
```

## Test Coverage

The test suite covers the following aspects of the Schieber card game:

### Database Utilities

- Connection management
- CRUD operations for all database tables
- Query functions for retrieving game data

### Card Utilities

- Card sorting (unten, oben, trumpf)
- Card manipulation (add, pop, move)
- Card set operations

### Game Utilities

- Game duration calculations
- Point calculation
- Game state checks
- Player order management

### Integration Tests

- Interaction between database and game utilities
- Interaction between card and game utilities

## Adding New Tests

When adding new features to the game, please follow these guidelines for writing tests:

1. **Unit Tests**: Create unit tests for new functions in the appropriate test file
2. **Integration Tests**: Add integration tests for features that involve multiple modules
3. **Test Coverage**: Ensure that all code paths are tested, including edge cases
4. **Isolation**: Keep tests isolated and avoid dependencies between tests

## Mocking

The tests use mock objects to simulate game components:

- `MockCard`: Simulates the Card class for testing card utilities
- In-memory SQLite database: Used for testing database operations without affecting real data

## Test Organization

Each test file follows this structure:

1. Import necessary modules
2. Define mock classes if needed
3. Create a test case class that inherits from `unittest.TestCase`
4. Define `setUp` and `tearDown` methods for test environment setup
5. Define test methods, each testing a specific aspect of the functionality
6. Add a main block to allow running the file directly

## Conventions

- Test method names should start with `test_` and describe what they test
- Use clear assertions with meaningful error messages
- Group related assertions within the same test method
- Use descriptive variable names that indicate their purpose
- Add comments to explain complex test logic