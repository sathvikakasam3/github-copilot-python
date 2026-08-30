from pathlib import Path
import sys

import pytest

STARTER_DIR = Path(__file__).resolve().parents[1]
if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))

import app as sudoku_app


@pytest.fixture
def client():
    sudoku_app.app.config.update(TESTING=True)
    sudoku_app.CURRENT["puzzle"] = None
    sudoku_app.CURRENT["solution"] = None

    with sudoku_app.app.test_client() as test_client:
        yield test_client

    sudoku_app.CURRENT["puzzle"] = None
    sudoku_app.CURRENT["solution"] = None
