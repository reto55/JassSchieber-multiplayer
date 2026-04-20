#!/usr/bin/env python3
"""Test runner for the Schieber card game.

Runs every test in `tests/` — both unittest.TestCase classes and pytest-style
function tests (e.g. `tests/test_game_session.py`). Delegates to pytest, which
discovers both styles, so a single `python run_tests.py` reports the full
picture.
"""
import sys
import pytest

if __name__ == "__main__":
    sys.exit(pytest.main(["tests", "-v"]))
