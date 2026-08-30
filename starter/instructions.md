# Sudoku Project Instructions

## General
- Build a maintainable Flask Sudoku application.
- Use clean, readable Python.
- Follow PEP 8 style.
- Use meaningful variable and function names.
- Keep functions small and focused.
- Avoid unnecessary duplication.
- Add comments where the logic is not obvious.
- Handle errors gracefully.

## Project Structure
- Keep Sudoku game logic separate from Flask routes.
- Keep frontend JavaScript separate from HTML.
- Keep styling in CSS files.
- Prefer reusable functions and modules.

## Sudoku Logic
- The board must always be a valid 9x9 Sudoku.
- Generated puzzles must have exactly one solution.
- Easy, Medium, and Hard difficulties should have different numbers of prefilled cells.
- Prefilled and hint-filled cells must be locked.
- User entries must be validated.

## Features
The application should support:
- Easy, Medium, Hard difficulty
- Timer
- Hint
- Check Puzzle
- Completion message
- Top 10 leaderboard
- Local storage
- Dark mode

## Frontend
- Make the interface responsive.
- Support desktop and mobile screens.
- Support light and dark modes.
- Use alternating styling for the 3x3 Sudoku boxes.
- Keep controls readable and accessible.

## Testing
- Do not remove existing tests without a good reason.
- Run tests after significant changes.
- Add tests for important Sudoku logic.