from pathlib import Path
import sys

STARTER_DIR = Path(__file__).resolve().parents[1]
if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))

import sudoku_logic as sl


def test_create_empty_board_shape_and_values():
    board = sl.create_empty_board()
    assert len(board) == sl.SIZE
    assert all(len(row) == sl.SIZE for row in board)
    assert all(cell == sl.EMPTY for row in board for cell in row)


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
