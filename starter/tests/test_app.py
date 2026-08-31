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


def test_index_includes_visible_timer(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'id="timer-value"' in response.data
    assert b'00:00' in response.data


def test_index_includes_theme_toggle(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'id="theme-toggle"' in response.data
    assert b'Dark mode' in response.data


def test_index_includes_leaderboard_and_score_form(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'id="score-form"' in response.data
    assert b'id="leaderboard-table"' in response.data
    assert b'/static/leaderboard.js' in response.data


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
    assert response.get_json() == {"puzzle": puzzle, "solution": solution, "hints_used": 0}


def test_new_with_query_clues_updates_current_store(client, monkeypatch):
    puzzle = _board_with_value(0)
    solution = _board_with_value(9)

    def fake_generate(clues):
        assert clues == 40
        return puzzle, solution

    monkeypatch.setattr(sudoku_logic, "generate_puzzle", fake_generate)

    response = client.get("/new?clues=40")
    assert response.status_code == 200
    assert response.get_json() == {"puzzle": puzzle, "solution": solution, "hints_used": 0}
    assert sudoku_app.CURRENT["puzzle"] == puzzle
    assert sudoku_app.CURRENT["solution"] == solution
    assert sudoku_app.CURRENT["hints_used"] == 0


def test_new_with_difficulty_maps_to_expected_clues(client, monkeypatch):
    seen = {}

    puzzle = _board_with_value(0)
    solution = _board_with_value(7)

    def fake_generate(clues):
        seen["clues"] = clues
        return puzzle, solution

    monkeypatch.setattr(sudoku_logic, "generate_puzzle", fake_generate)

    response = client.get("/new?difficulty=hard")
    assert response.status_code == 200
    assert seen["clues"] == 30
    assert response.get_json() == {"puzzle": puzzle, "solution": solution, "hints_used": 0}


def test_new_rejects_unknown_difficulty(client):
    response = client.get("/new?difficulty=impossible")

    assert response.status_code == 400
    assert response.get_json() == {"error": "unknown difficulty: impossible"}


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
    assert response.get_json() == {"incorrect": [[0, 0], [8, 8]], "solved": False}


def test_check_returns_solved_true_for_complete_board(client):
    solution = _board_with_value(4)
    sudoku_app.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": solution})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [], "solved": True}


def test_hint_returns_one_empty_cell_and_tracks_hint_count(client):
    puzzle = _board_with_value(0)
    solution = [[(row * sudoku_logic.SIZE + col) % 9 + 1 for col in range(sudoku_logic.SIZE)] for row in range(sudoku_logic.SIZE)]
    sudoku_app.CURRENT["puzzle"] = puzzle
    sudoku_app.CURRENT["solution"] = solution

    board = _board_with_value(0)
    board[0][0] = 5

    response = client.post("/hint", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {"row": 0, "col": 1, "value": solution[0][1], "hints_used": 1}
    assert sudoku_app.CURRENT["hints_used"] == 1


def test_hint_rejects_when_board_has_no_empty_cells(client):
    solution = _board_with_value(3)
    sudoku_app.CURRENT["solution"] = solution

    response = client.post("/hint", json={"board": solution})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No empty cells available"}
