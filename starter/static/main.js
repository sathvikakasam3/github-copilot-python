// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;

const gameState = {
  puzzle: [],
  solution: [],
  lockedCells: new Set(),
  hintsUsed: 0,
  completed: false,
  timerIntervalId: null,
  elapsedSeconds: 0,
  activeGameRequestId: 0,
};

window.sudokuGameState = gameState;

function cellKey(row, col) {
  return row * SIZE + col;
}

function getSelectedDifficulty() {
  const selector = document.getElementById('difficulty');
  return selector ? selector.value : 'medium';
}

function setMessage(text, tone = 'info') {
  const message = document.getElementById('message');
  message.textContent = text;
  message.dataset.tone = tone;
}

function updateHintCounter() {
  const hintCount = document.getElementById('hint-count');
  if (hintCount) {
    hintCount.textContent = String(gameState.hintsUsed);
  }
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timer = document.getElementById('timer-value');
  if (timer) {
    timer.textContent = formatTime(gameState.elapsedSeconds);
  }
}

function stopTimer() {
  if (gameState.timerIntervalId !== null) {
    window.clearInterval(gameState.timerIntervalId);
    gameState.timerIntervalId = null;
  }
}

function resetTimer() {
  stopTimer();
  gameState.elapsedSeconds = 0;
  updateTimerDisplay();
}

function startTimer() {
  stopTimer();
  gameState.elapsedSeconds = 0;
  updateTimerDisplay();

  gameState.timerIntervalId = window.setInterval(() => {
    if (gameState.completed) {
      stopTimer();
      return;
    }

    gameState.elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function getBoardFromInputs() {
  const inputs = document.querySelectorAll('.sudoku-cell');
  const board = [];

  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let col = 0; col < SIZE; col++) {
      const input = inputs[cellKey(row, col)];
      board[row][col] = input && input.value ? parseInt(input.value, 10) : 0;
    }
  }

  return board;
}

function clearIncorrectHighlights() {
  document.querySelectorAll('.sudoku-cell').forEach((input) => {
    input.classList.remove('incorrect');
  });
}

function lockBoard() {
  document.querySelectorAll('.sudoku-cell').forEach((input) => {
    input.readOnly = true;
    input.dataset.locked = 'true';
  });
}

function markCompletion() {
  if (gameState.completed) {
    return;
  }

  gameState.completed = true;
  stopTimer();
  lockBoard();
  setMessage(`Congratulations! Puzzle complete. Hints used: ${gameState.hintsUsed}.`, 'success');
  window.dispatchEvent(new CustomEvent('sudoku:completed', {
    detail: {
      hintsUsed: gameState.hintsUsed,
      completedAt: new Date().toISOString(),
    },
  }));
}

function checkForCompletion() {
  if (gameState.completed || gameState.solution.length !== SIZE) {
    return;
  }

  const board = getBoardFromInputs();
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      if (board[row][col] === 0 || board[row][col] !== gameState.solution[row][col]) {
        return;
      }
    }
  }

  markCompletion();
}

function prepareCell(input, row, col, value, lockedClass) {
  input.type = 'text';
  input.maxLength = 1;
  input.className = 'sudoku-cell';
  input.dataset.row = row;
  input.dataset.col = col;
  input.dataset.locked = lockedClass ? 'true' : 'false';
  input.readOnly = Boolean(lockedClass);
  input.value = value === 0 ? '' : String(value);

  if (lockedClass) {
    input.classList.add(lockedClass);
  }

  input.addEventListener('input', (event) => {
    if (event.target.readOnly) {
      return;
    }

    event.target.value = event.target.value.replace(/[^1-9]/g, '').slice(0, 1);
    event.target.classList.remove('incorrect');
    setMessage('', 'info');
    checkForCompletion();
  });
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';

  for (let row = 0; row < SIZE; row++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';

    for (let col = 0; col < SIZE; col++) {
      const input = document.createElement('input');
      prepareCell(input, row, col, 0, null);
      rowDiv.appendChild(input);
    }

    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puzzle) {
  gameState.puzzle = puzzle;
  gameState.lockedCells = new Set();
  gameState.completed = false;

  createBoardElement();

  const inputs = document.querySelectorAll('.sudoku-cell');
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const idx = cellKey(row, col);
      const input = inputs[idx];
      const value = puzzle[row][col];

      input.className = 'sudoku-cell';
      input.dataset.row = row;
      input.dataset.col = col;
      input.dataset.locked = value === 0 ? 'false' : 'true';
      input.readOnly = value !== 0;
      input.value = value === 0 ? '' : String(value);

      if (value !== 0) {
        input.classList.add('prefilled');
        gameState.lockedCells.add(idx);
      }
    }
  }

  clearIncorrectHighlights();
  updateHintCounter();
  setMessage('', 'info');
  updateTimerDisplay();
}

async function newGame() {
  try {
    const requestId = gameState.activeGameRequestId + 1;
    gameState.activeGameRequestId = requestId;

    const difficulty = getSelectedDifficulty();
    const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
    const data = await res.json();

    if (requestId !== gameState.activeGameRequestId) {
      return;
    }

    if (!res.ok || data.error) {
      setMessage(data.error || 'Unable to start a new game.', 'error');
      return;
    }

    gameState.solution = data.solution;
    gameState.hintsUsed = data.hints_used ?? 0;
    renderPuzzle(data.puzzle);
    updateHintCounter();
    startTimer();
  } catch (error) {
    setMessage('Unable to start a new game.', 'error');
  }
}

function checkSolution() {
  if (gameState.solution.length !== SIZE) {
    setMessage('Start a game first.', 'error');
    return;
  }

  const board = getBoardFromInputs();
  clearIncorrectHighlights();

  const incorrectCells = [];
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const key = cellKey(row, col);
      const value = board[row][col];
      if (gameState.lockedCells.has(key) || value === 0) {
        continue;
      }

      if (value !== gameState.solution[row][col]) {
        incorrectCells.push(key);
      }
    }
  }

  incorrectCells.forEach((idx) => {
    const input = document.querySelectorAll('.sudoku-cell')[idx];
    if (input) {
      input.classList.add('incorrect');
    }
  });

  if (incorrectCells.length === 0) {
    setMessage('All entered values are correct so far.', 'success');
    checkForCompletion();
  } else {
    setMessage('Some entered values are incorrect.', 'error');
  }
}

async function requestHint() {
  if (gameState.completed) {
    return;
  }

  if (gameState.solution.length !== SIZE) {
    setMessage('Start a game first.', 'error');
    return;
  }

  const board = getBoardFromInputs();

  try {
    const res = await fetch('/hint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board }),
    });
    const data = await res.json();

    if (!res.ok || data.error) {
      setMessage(data.error || 'No empty cell could be filled.', 'error');
      return;
    }

    const idx = cellKey(data.row, data.col);
    const input = document.querySelectorAll('.sudoku-cell')[idx];
    if (!input || input.readOnly || input.value) {
      setMessage('No empty cell could be filled.', 'error');
      return;
    }

    input.value = String(data.value);
    input.readOnly = true;
    input.dataset.locked = 'true';
    input.classList.remove('incorrect');
    input.classList.add('hinted');
    gameState.lockedCells.add(idx);
    gameState.hintsUsed = data.hints_used;
    updateHintCounter();
    setMessage(`Hint placed. Hints used: ${gameState.hintsUsed}.`, 'info');
    checkForCompletion();
  } catch (error) {
    setMessage('Unable to request a hint.', 'error');
  }
}

function resetGameState() {
  gameState.puzzle = [];
  gameState.solution = [];
  gameState.lockedCells = new Set();
  gameState.hintsUsed = 0;
  gameState.completed = false;
  resetTimer();
  updateHintCounter();
}

window.addEventListener('load', () => {
  resetGameState();
  document.getElementById('difficulty').addEventListener('change', newGame);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  newGame();
});