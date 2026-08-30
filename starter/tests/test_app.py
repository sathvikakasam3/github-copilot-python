from pathlib import Path
import sys

STARTER_DIR = Path(__file__).resolve().parents[1]
if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))

import app as sudoku_app
import sudoku_logic


def _board_with_value(value):
    return [[value for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]


def test_index_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sudoku Game" in response.data


def test_new_uses_default_clues_when_not_provided(client, monkeypatch):
    seen = {}

    puzzle = _board_with_value(0)
    solution = _board_with_value(1)

    def fake_generate(clues):
        seen["clues"] = clues
        return puzzle, solution

    monkeypatch.setattr(sudoku_logic, "generate_puzzle", fake_generate)

    response = client.get("/new")
    assert response.status_code == 200
    assert seen["clues"] == 35
    assert response.get_json() == {"puzzle": puzzle}


def test_new_with_query_clues_updates_current_store(client, monkeypatch):
    puzzle = _board_with_value(0)
    solution = _board_with_value(9)

    def fake_generate(clues):
        assert clues == 40
        return puzzle, solution

    monkeypatch.setattr(sudoku_logic, "generate_puzzle", fake_generate)

    response = client.get("/new?clues=40")
    assert response.status_code == 200
    assert response.get_json() == {"puzzle": puzzle}
    assert sudoku_app.CURRENT["puzzle"] == puzzle
    assert sudoku_app.CURRENT["solution"] == solution


def test_check_returns_400_if_no_game_in_progress(client):
    board = _board_with_value(0)
    response = client.post("/check", json={"board": board})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No game in progress"}


def test_check_returns_incorrect_coordinates(client):
    solution = _board_with_value(1)
    sudoku_app.CURRENT["solution"] = solution

    board = _board_with_value(1)
    board[0][0] = 2
    board[8][8] = 3

    response = client.post("/check", json={"board": board})
    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [[0, 0], [8, 8]]}
