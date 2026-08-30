import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 30,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def _find_best_empty_cell(board):
    best_row = None
    best_col = None
    best_candidates = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue

            candidates = [num for num in range(1, SIZE + 1) if is_safe(board, row, col, num)]
            if not candidates:
                return row, col, []

            if best_candidates is None or len(candidates) < len(best_candidates):
                best_row = row
                best_col = col
                best_candidates = candidates

                if len(best_candidates) == 1:
                    return best_row, best_col, best_candidates

    if best_candidates is None:
        return None, None, None

    return best_row, best_col, best_candidates


def count_solutions(board, limit=2):
    if limit < 1:
        raise ValueError('limit must be at least 1')

    row, col, candidates = _find_best_empty_cell(board)
    if candidates is None:
        return 1
    if not candidates:
        return 0

    solution_count = 0
    for candidate in candidates:
        board[row][col] = candidate
        solution_count += count_solutions(board, limit=limit - solution_count)
        board[row][col] = EMPTY

        if solution_count >= limit:
            return solution_count

    return solution_count


def _count_filled_cells(board):
    return sum(1 for row in board for cell in row if cell != EMPTY)


def remove_cells(board, clues):
    if clues < 0 or clues > SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')

    current_clues = _count_filled_cells(board)
    if current_clues < clues:
        raise ValueError('board has fewer clues than requested')

    while current_clues > clues:
        filled_positions = [
            (row, col)
            for row in range(SIZE)
            for col in range(SIZE)
            if board[row][col] != EMPTY
        ]
        random.shuffle(filled_positions)

        removed_in_pass = 0
        for row, col in filled_positions:
            if board[row][col] == EMPTY:
                continue

            value = board[row][col]
            board[row][col] = EMPTY
            if count_solutions(board, limit=2) == 1:
                current_clues -= 1
                removed_in_pass += 1
                if current_clues == clues:
                    return
            else:
                board[row][col] = value

        if removed_in_pass == 0:
            break


def get_clues_for_difficulty(difficulty):
    if difficulty is None:
        difficulty = 'medium'

    normalized = str(difficulty).strip().lower()
    if normalized not in DIFFICULTY_CLUES:
        raise ValueError(f"unknown difficulty: {difficulty}")

    return DIFFICULTY_CLUES[normalized]


def generate_puzzle_for_difficulty(difficulty='medium'):
    clues = get_clues_for_difficulty(difficulty)
    return generate_puzzle(clues)

def generate_puzzle(clues=35):
    if clues < 0 or clues > SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
