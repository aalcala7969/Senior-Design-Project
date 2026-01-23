// Game state
let currentScreen = 'title-screen';
let tttBoard = ['', '', '', '', '', '', '', '', ''];
let tttCurrentPlayer = 'X';
let tttVsAI = false;
let tttGameOver = false;

// Hangman game state
let hangmanWord = ''; //test changes
let correctGuesses = new Set();
let wrongGuesses = new Set();
let hangmanGameOver = false;

// Word list for hangman
const HANGMAN_WORDS = [
    "python", "gpu", "jestonnano", "matrix", "serial",
    "school", "sdsu", "robot", "thread", "gui",
    "professor", "hand", "arm", "sensor", "display",
];

const MAX_MISSES = 6;

// Screen management
function showScreen(screenId) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Show target screen
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');
        currentScreen = screenId;
    }
}

function closeApp() {
    if (confirm('Are you sure you want to exit?')) {
        window.close();
    }
}

// Tic Tac Toe functions
const WIN_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
    [0, 4, 8], [2, 4, 6]  // diagonals
];

function checkWinner(board) {
    for (let [a, b, c] of WIN_LINES) {
        if (board[a] && board[a] === board[b] && board[b] === board[c]) {
            return board[a];
        }
    }
    return null;
}

function isDraw(board) {
    return board.every(cell => cell !== '') && !checkWinner(board);
}

function validMoves(board) {
    return board.map((cell, index) => cell === '' ? index : null).filter(val => val !== null);
}

function minimax(board, player, ai, human) {
    const winner = checkWinner(board);
    if (winner === ai) return [1, null];
    if (winner === human) return [-1, null];
    if (isDraw(board)) return [0, null];

    const moves = validMoves(board);
    if (player === ai) {
        let bestScore = -2;
        let bestMove = null;
        for (let m of moves) {
            board[m] = ai;
            const [score] = minimax(board, human, ai, human);
            board[m] = '';
            if (score > bestScore) {
                bestScore = score;
                bestMove = m;
                if (score === 1) break;
            }
        }
        return [bestScore, bestMove];
    } else {
        let bestScore = 2;
        let bestMove = null;
        for (let m of moves) {
            board[m] = human;
            const [score] = minimax(board, ai, ai, human);
            board[m] = '';
            if (score < bestScore) {
                bestScore = score;
                bestMove = m;
                if (score === -1) break;
            }
        }
        return [bestScore, bestMove];
    }
}

function startTicTacToe(vsAI) {
    // If whiteboard mode (vsAI = false), show message instead
    if (!vsAI) {
        showWhiteboardMessage();
        return;
    }
    
    tttVsAI = vsAI;
    tttBoard = ['', '', '', '', '', '', '', '', ''];
    tttCurrentPlayer = 'X';
    tttGameOver = false;
    showScreen('ttt-game-screen');
    renderTicTacToeBoard();
    updateTicTacToeStatus();
}

function renderTicTacToeBoard() {
    const board = document.getElementById('ttt-board');
    board.innerHTML = '';
    
    for (let i = 0; i < 9; i++) {
        const cell = document.createElement('div');
        cell.className = 'ttt-cell';
        cell.textContent = tttBoard[i];
        if (tttBoard[i] === 'X') cell.classList.add('x');
        if (tttBoard[i] === 'O') cell.classList.add('o');
        if (tttBoard[i] !== '' || tttGameOver) cell.classList.add('disabled');
        
        cell.addEventListener('click', () => makeTicTacToeMove(i, cell));
        board.appendChild(cell);
    }
}

function makeTicTacToeMove(index, cell) {
    if (tttBoard[index] !== '' || tttGameOver) return;
    
    tttBoard[index] = tttCurrentPlayer;
    cell.textContent = tttCurrentPlayer;
    cell.classList.add(tttCurrentPlayer.toLowerCase());
    cell.classList.add('disabled');
    
    const winner = checkWinner(tttBoard);
    if (winner) {
        tttGameOver = true;
        showModal(`Player ${winner} wins!`, 'Game Over');
        return;
    }
    
    if (isDraw(tttBoard)) {
        tttGameOver = true;
        showModal("It's a draw!", 'Game Over');
        return;
    }
    
    tttCurrentPlayer = tttCurrentPlayer === 'X' ? 'O' : 'X';
    updateTicTacToeStatus();
    
    if (tttVsAI && tttCurrentPlayer === 'O' && !tttGameOver) {
        setTimeout(() => makeAIMove(), 500);
    }
}

function makeAIMove() {
    const [, move] = minimax(tttBoard, 'O', 'O', 'X');
    if (move !== null) {
        const cells = document.querySelectorAll('.ttt-cell');
        makeTicTacToeMove(move, cells[move]);
    }
}

function updateTicTacToeStatus() {
    const status = document.getElementById('ttt-status');
    status.textContent = `Player ${tttCurrentPlayer}'s Turn`;
}

// Hangman functions
function startHangman(againstRobot = true) {
    // If whiteboard mode (againstRobot = false), show message instead
    if (!againstRobot) {
        showWhiteboardMessage();
        return;
    }
    
    // againstRobot: true = play against robot, false = play on whiteboard
    hangmanWord = HANGMAN_WORDS[Math.floor(Math.random() * HANGMAN_WORDS.length)].toLowerCase();
    correctGuesses.clear();
    wrongGuesses.clear();
    hangmanGameOver = false;
    showScreen('hangman-game-screen');
    renderHangman();
}

function renderHangman() {
    // Update word display
    const wordDisplay = document.getElementById('word-display');
    wordDisplay.textContent = hangmanWord
        .split('')
        .map(char => correctGuesses.has(char) ? char.toUpperCase() : '_')
        .join(' ');
    
    // Update wrong guesses
    const wrongGuessesEl = document.getElementById('wrong-guesses');
    wrongGuessesEl.textContent = wrongGuesses.size > 0 
        ? Array.from(wrongGuesses).sort().join(', ').toUpperCase()
        : '-';
    
    // Update lives
    document.getElementById('lives').textContent = MAX_MISSES - wrongGuesses.size;
    
    // Create letter buttons
    const letterGrid = document.getElementById('letter-grid');
    letterGrid.innerHTML = '';
    
    for (let letter of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') {
        const btn = document.createElement('button');
        btn.className = 'letter-btn';
        btn.textContent = letter;
        
        const letterLower = letter.toLowerCase();
        if (correctGuesses.has(letterLower) || wrongGuesses.has(letterLower)) {
            btn.classList.add('disabled');
            if (correctGuesses.has(letterLower)) {
                btn.classList.add('correct');
            } else {
                btn.classList.add('wrong');
            }
        }
        
        btn.addEventListener('click', () => guessLetter(letterLower, btn));
        letterGrid.appendChild(btn);
    }
    
    // Check win/lose
    if (Array.from(new Set(hangmanWord)).every(char => correctGuesses.has(char))) {
        hangmanGameOver = true;
        showModal(`You won! The word was "${hangmanWord.toUpperCase()}"`, 'You Won!');
    } else if (wrongGuesses.size >= MAX_MISSES) {
        hangmanGameOver = true;
        showModal(`You lost! The word was "${hangmanWord.toUpperCase()}"`, 'Game Over');
    }
}

function guessLetter(letter, button) {
    if (hangmanGameOver || correctGuesses.has(letter) || wrongGuesses.has(letter)) {
        return;
    }
    
    const statusMessage = document.getElementById('status-message');
    
    if (hangmanWord.includes(letter)) {
        correctGuesses.add(letter);
        button.classList.add('correct', 'disabled');
        statusMessage.textContent = `Good guess! '${letter.toUpperCase()}' is in the word!`;
    } else {
        wrongGuesses.add(letter);
        button.classList.add('wrong', 'disabled');
        statusMessage.textContent = `'${letter.toUpperCase()}' is not in the word.`;
    }
    
    renderHangman();
}

// Whiteboard message function
function showWhiteboardMessage() {
    showModal('Look at whiteboard', 'Whiteboard Mode');
}

// Modal functions
function showModal(message, title) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-message').textContent = message;
    document.getElementById('game-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('game-modal').classList.remove('active');
    if (currentScreen === 'ttt-game-screen') {
        startTicTacToe(tttVsAI);
    } else if (currentScreen === 'hangman-game-screen') {
        startHangman();
    }
}

// Close modal on outside click
document.getElementById('game-modal').addEventListener('click', (e) => {
    if (e.target.id === 'game-modal') {
        closeModal();
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showScreen('title-screen');
});

