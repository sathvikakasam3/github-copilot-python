from pathlib import Path
import sys
import random

STARTER_DIR = Path(__file__).resolve().parents[1]
if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))

import sudoku_logic as sl


def test_create_empty_board_shape_and_values():
    board = sl.create_empty_board()
    assert len(board) == sl.SIZE
    assert all(len(row) == sl.SIZE for row in board)
    assert all(cell == sl.EMPTY for row in board for cell in row)


def test_board_matches_solution_and_completion_helpers():
    solved_board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    board = sl.deep_copy(solved_board)

    assert sl.board_matches_solution(board, solved_board) is True
    assert sl.is_board_complete(board, solved_board) is True

    board[0][0] = sl.EMPTY
    assert sl.board_matches_solution(board, solved_board) is False
    assert sl.is_board_complete(board, solved_board) is False


def test_get_incorrect_cells_and_hint_cell_helpers():
    solution = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 1, 5, 6, 4, 8, 9, 7],
        [5, 6, 4, 8, 9, 7, 2, 3, 1],
        [8, 9, 7, 2, 3, 1, 5, 6, 4],
        [3, 1, 2, 6, 4, 5, 9, 7, 8],
        [6, 4, 5, 9, 7, 8, 3, 1, 2],
        [9, 7, 8, 3, 1, 2, 6, 4, 5],
    ]
    board = sl.deep_copy(solution)
    board[0][0] = 9
    board[0][1] = sl.EMPTY

    assert sl.get_incorrect_cells(board, solution) == [[0, 0]]
    assert sl.get_hint_cell(board, solution) == {"row": 0, "col": 1, "value": 2}

    full_board = sl.deep_copy(solution)
    assert sl.get_hint_cell(full_board, solution) is None


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sl.create_empty_board()
    board[0][0] = 5
    assert sl.is_safe(board, 0, 1, 5) is False  # row conflict
    assert sl.is_safe(board, 1, 0, 5) is False  # column conflict
    assert sl.is_safe(board, 1, 1, 5) is False  # box conflict
    assert sl.is_safe(board, 0, 1, 4) is True


def test_fill_board_produces_valid_complete_grid():
    board = sl.create_empty_board()
    assert sl.fill_board(board) is True

    expected = set(range(1, sl.SIZE + 1))

    for row in board:
        assert set(row) == expected

    for c in range(sl.SIZE):
        col_vals = {board[r][c] for r in range(sl.SIZE)}
        assert col_vals == expected


def test_count_solutions_returns_one_for_single_empty_cell_board():
    solved_board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    puzzle = sl.deep_copy(solved_board)
    puzzle[0][0] = sl.EMPTY

    assert sl.count_solutions(puzzle, limit=2) == 1


def test_get_clues_for_difficulty_maps_expected_counts():
    assert sl.get_clues_for_difficulty('easy') == 45
    assert sl.get_clues_for_difficulty('medium') == 35
    assert sl.get_clues_for_difficulty('hard') == 30


def test_generate_puzzle_for_difficulty_uses_difficulty_clue_counts():
    random.seed(0)

    for difficulty, expected_clues in [('easy', 45), ('medium', 35), ('hard', 30)]:
        puzzle, solution = sl.generate_puzzle_for_difficulty(difficulty)
        non_empty = sum(1 for row in puzzle for cell in row if cell != sl.EMPTY)
        assert non_empty == expected_clues
        assert sl.count_solutions(puzzle, limit=2) == 1

        for i in range(sl.SIZE):
            for j in range(sl.SIZE):
                if puzzle[i][j] != sl.EMPTY:
                    assert puzzle[i][j] == solution[i][j]


def test_generate_puzzle_clue_count_and_solution_alignment():
    clues = 35
    puzzle, solution = sl.generate_puzzle(clues)

    assert len(puzzle) == sl.SIZE
    assert len(solution) == sl.SIZE
    assert all(len(row) == sl.SIZE for row in puzzle)
    assert all(len(row) == sl.SIZE for row in solution)

    non_empty = sum(1 for row in puzzle for cell in row if cell != sl.EMPTY)
    assert non_empty == clues

    for i in range(sl.SIZE):
        for j in range(sl.SIZE):
            if puzzle[i][j] != sl.EMPTY:
                assert puzzle[i][j] == solution[i][j]


def test_generate_puzzle_has_exactly_one_solution():
    random.seed(0)

    puzzle, _ = sl.generate_puzzle(35)

    assert sl.count_solutions(puzzle, limit=2) == 1
