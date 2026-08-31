const LEADERBOARD_STORAGE_KEY = 'sudokoLeaderBoard';
const LEADERBOARD_LIMIT = 10;
const VALID_DIFFICULTIES = new Set(['easy', 'medium', 'hard']);

function normalizeScore(score) {
  if (!score || typeof score !== 'object') {
    return null;
  }

  const playerName = typeof score.playerName === 'string' ? score.playerName.trim() : '';
  const completionTime = Number(score.completionTime);
  const hintsUsed = Number(score.hintsUsed);
  const difficulty = typeof score.difficulty === 'string' ? score.difficulty : '';

  if (!playerName || !Number.isInteger(completionTime) || completionTime < 0
      || !Number.isInteger(hintsUsed) || hintsUsed < 0
      || !VALID_DIFFICULTIES.has(difficulty)) {
    return null;
  }

  return {
    playerName: playerName.slice(0, 40),
    completionTime,
    difficulty,
    hintsUsed,
  };
}

function sortScores(scores) {
  return scores.sort((first, second) => first.completionTime - second.completionTime);
}

function getLeaderboardScores() {
  try {
    const storedScores = window.localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    if (!storedScores) {
      return [];
    }

    const parsedScores = JSON.parse(storedScores);
    if (!Array.isArray(parsedScores)) {
      return [];
    }

    return sortScores(parsedScores.map(normalizeScore).filter(Boolean)).slice(0, LEADERBOARD_LIMIT);
  } catch (error) {
    return [];
  }
}

function addLeaderboardScore(score) {
  const normalizedScore = normalizeScore(score);
  if (!normalizedScore) {
    return getLeaderboardScores();
  }

  const scores = getLeaderboardScores();
  scores.push(normalizedScore);
  const topScores = sortScores(scores).slice(0, LEADERBOARD_LIMIT);

  try {
    window.localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(topScores));
  } catch (error) {
    // Storage can be unavailable in private browsing or restrictive environments.
  }

  return topScores;
}

window.sudokuLeaderboard = {
  addScore: addLeaderboardScore,
  getScores: getLeaderboardScores,
};
