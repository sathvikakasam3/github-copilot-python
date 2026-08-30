from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
}


def _reset_current_game(puzzle, solution):
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    clues_param = request.args.get('clues')

    try:
        if difficulty is not None:
            clues = sudoku_logic.get_clues_for_difficulty(difficulty)
        elif clues_param is not None:
            clues = int(clues_param)
        else:
            clues = sudoku_logic.get_clues_for_difficulty('medium')
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    _reset_current_game(puzzle, solution)
    return jsonify({'puzzle': puzzle, 'solution': solution, 'hints_used': 0})


@app.route('/hint', methods=['POST'])
def request_hint():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    hint = sudoku_logic.get_hint_cell(board, solution)
    if hint is None:
        return jsonify({'error': 'No empty cells available'}), 400

    CURRENT['hints_used'] += 1
    hint['hints_used'] = CURRENT['hints_used']
    return jsonify(hint)

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = sudoku_logic.get_incorrect_cells(board, solution)
    solved = sudoku_logic.is_board_complete(board, solution)
    return jsonify({'incorrect': incorrect, 'solved': solved})

if __name__ == '__main__':
    app.run(debug=True)