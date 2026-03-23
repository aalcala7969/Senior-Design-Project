"""
Robotic Gaming Arm - Multi-Game Application

This app provides a touch-friendly interface for playing games with a robotic arm.
It includes:
- Tic Tac Toe (2-player or vs AI)
- Hangman (touch-friendly letter buttons)

The app uses Kivy for the GUI, which is designed to work well with touch screens.
All screens are managed by a ScreenManager that handles navigation between them.
"""

# Kivy imports - these are the GUI framework components we need
from kivy.app import App  # Main app class
from kivy.lang import Builder  # For loading UI layouts from strings
from kivy.uix.screenmanager import ScreenManager, Screen  # For multiple screens/pages
from kivy.uix.screenmanager import SlideTransition  # Screen transition effect
from kivy.uix.button import Button  # Clickable buttons
from kivy.uix.popup import Popup  # Popup windows
from kivy.uix.label import Label  # Text labels
from kivy.uix.boxlayout import BoxLayout  # Container that arranges widgets in a line
from kivy.uix.gridlayout import GridLayout  # Container that arranges widgets in a grid
from kivy.core.window import Window
import os
import random
import string
import subprocess
import sys

# Word list for hangman game - these are the words the game picks from
HANGMAN_WORDS = [
    "python", "gpu", "jestonnano", "matrix", "serial", 
    "school", "sdsu", "robot", "thread", "gui",
    "professor", "hand", "arm", "sensor", "display",
]

MAX_MISSES = 6  # How many wrong guesses you get before losing

# All the UI stuff is defined here as a string
# Could split this into a separate .kv file but this works fine for now
Builder.load_string("""
# Base button styling - flat, modern look
<StyledButton@Button>:
    background_normal: ''
    background_color: 0.15, 0.15, 0.2, 1
    color: 0.95, 0.95, 1.0, 1
    font_size: 22
    bold: True
    border: (0, 0, 0, 0)

<CardButton@Button>:
    background_normal: ''
    background_color: 0.12, 0.12, 0.18, 1
    color: 0.95, 0.95, 1.0, 1
    font_size: 24
    bold: True
    border: (2, 2, 2, 2)
    border_color: (0.25, 0.25, 0.35, 1)

<TitleScreen>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    ScrollView:
        do_scroll_x: False
        bar_width: 8
        BoxLayout:
            orientation: 'vertical'
            spacing: 28
            padding: [40, 36, 40, 36]
            size_hint_y: None
            height: self.minimum_height
            
            Label:
                text: 'RGA'
                font_size: 96
                size_hint_y: None
                height: 130
                color: 0.95, 0.32, 0.32, 1
                bold: True
                outline_color: 0.7, 0.15, 0.15, 0.9
                outline_width: 2
            
            Label:
                text: 'Robotic Gaming Arm'
                font_size: 32
                size_hint_y: None
                height: 48
                color: 0.85, 0.88, 0.95, 1
                bold: True
            
            Label:
                text: 'We hope you enjoy!'
                font_size: 22
                size_hint_y: None
                height: 36
                color: 1, 1, 1, 1
            
            Widget:
                size_hint_y: None
                height: 24
            
            StyledButton:
                text: "Let's Play!"
                font_size: 48
                size_hint_y: None
                height: 110
                background_color: 0.15, 0.52, 0.82, 1
                on_press: root.manager.current = 'menu'
            
            StyledButton:
                text: 'Maybe Later'
                font_size: 26
                size_hint_y: None
                height: 64
                background_color: 0.22, 0.24, 0.32, 1
                on_press: app.stop()

<MenuScreen>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    ScrollView:
        do_scroll_x: False
        bar_width: 8
        BoxLayout:
            orientation: 'vertical'
            spacing: 20
            padding: [36, 28, 36, 28]
            size_hint_y: None
            height: self.minimum_height
            
            Label:
                text: 'RGA'
                font_size: 64
                size_hint_y: None
                height: 86
                color: 0.95, 0.32, 0.32, 1
                bold: True
            
            Label:
                text: 'What would you like to play?'
                font_size: 28
                size_hint_y: None
                height: 44
                color: 0.95, 0.95, 1.0, 1
                bold: True
            
            GridLayout:
                cols: 2
                spacing: 16
                size_hint_y: None
                height: 216
                row_default_height: 100
                row_force_default: True
                
                CardButton:
                    text: 'Tic Tac Toe'
                    background_color: 0.12, 0.3, 0.38, 1
                    on_press: root.manager.current = 'ttt'
                
                CardButton:
                    text: 'Hangman'
                    background_color: 0.1, 0.35, 0.35, 1
                    on_press: root.manager.current = 'hm'
                
                CardButton:
                    text: 'Connect 4'
                    background_color: 0.08, 0.32, 0.4, 1
                    on_press: root.show_under_development()
                
                CardButton:
                    text: 'Dots & Boxes'
                    background_color: 0.1, 0.38, 0.32, 1
                    on_press: root.show_under_development()
            
            StyledButton:
                text: '← Back'
                font_size: 20
                size_hint_y: None
                height: 50
                background_color: 0.85, 0.2, 0.2, 1
                on_press: root.manager.current = 'title'

<TicTacToeScreen>:
    canvas.before:
        Color:
            rgba: 0.04, 0.04, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 24
        padding: [50, 60, 50, 60]
        
        Label:
            text: 'Tic Tac Toe'
            font_size: 44
            size_hint_y: None
            height: 65
            color: 0.95, 0.95, 1.0, 1
            bold: True
        
        Label:
            text: 'Get three in a row to win!'
            font_size: 22
            size_hint_y: None
            height: 38
            color: 0.72, 0.72, 0.85, 1
        
        Widget:
            size_hint_y: 0.25
        
        Label:
            text: 'Choose your game mode:'
            font_size: 24
            size_hint_y: None
            height: 40
            color: 0.88, 0.88, 0.95, 1
        
        StyledButton:
            text: 'Two Players'
            font_size: 26
            size_hint_y: None
            height: 70
            background_color: 0.25, 0.65, 0.5, 1
            on_press: root.start_game(vs_ai=False)
        
        # Play vs Robotic Arm goes to difficulty selection first
        StyledButton:
            text: 'Play vs Robotic Arm'
            font_size: 26
            size_hint_y: None
            height: 70
            background_color: 0.2, 0.5, 0.8, 1
            on_press: root.manager.current = 'ttt_difficulty'
        
        Widget:
            size_hint_y: 0.25
        
        StyledButton:
            text: '← Back to Menu'
            font_size: 20
            size_hint_y: None
            height: 50
            background_color: 0.18, 0.18, 0.24, 1
            on_press: root.manager.current = 'menu'

# Difficulty selection screen (easy, medium, hard, impossible)
<TicTacToeDifficultyScreen>:
    canvas.before:
        Color:
            rgba: 0.04, 0.04, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 24
        padding: [50, 60, 50, 60]
        
        Label:
            text: 'Choose Difficulty'
            font_size: 44
            size_hint_y: None
            height: 65
            color: 0.95, 0.95, 1.0, 1
            bold: True
        
        Label:
            text: 'Select how smart the robotic arm plays'
            font_size: 22
            size_hint_y: None
            height: 38
            color: 0.72, 0.72, 0.85, 1
        
        Widget:
            size_hint_y: 0.2
        
        StyledButton:
            text: 'Easy'
            font_size: 26
            size_hint_y: None
            height: 65
            background_color: 0.25, 0.65, 0.45, 1
            on_press: root.start_with_difficulty('easy')
        
        StyledButton:
            text: 'Medium'
            font_size: 26
            size_hint_y: None
            height: 65
            background_color: 0.85, 0.6, 0.2, 1
            on_press: root.start_with_difficulty('medium')
        
        StyledButton:
            text: 'Hard'
            font_size: 26
            size_hint_y: None
            height: 65
            background_color: 0.85, 0.45, 0.2, 1
            on_press: root.start_with_difficulty('hard')
        
        StyledButton:
            text: 'Impossible'
            font_size: 26
            size_hint_y: None
            height: 65
            background_color: 0.85, 0.2, 0.2, 1
            on_press: root.start_with_difficulty('impossible')
        
        Widget:
            size_hint_y: 0.2
        
        StyledButton:
            text: '← Back'
            font_size: 20
            size_hint_y: None
            height: 50
            background_color: 0.18, 0.18, 0.24, 1
            on_press: root.manager.current = 'ttt'

<TicTacToeGameScreen>:
    canvas.before:
        Color:
            rgba: 0.04, 0.04, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 22
        padding: [35, 45, 35, 35]
        
        Label:
            id: status_label
            text: "Player X's Turn"
            font_size: 28
            size_hint_y: None
            height: 55
            color: 0.95, 0.95, 1.0, 1
            bold: True
        
        GridLayout:
            id: board
            rows: 3
            cols: 3
            spacing: 12
            size_hint_y: 1
            padding: [25, 25, 25, 25]
        
        StyledButton:
            text: '← Back to Menu'
            font_size: 20
            size_hint_y: None
            height: 50
            background_color: 0.18, 0.18, 0.24, 1
            on_press: root.manager.current = 'menu'

<HangmanScreen>:
    canvas.before:
        Color:
            rgba: 0.04, 0.04, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 28
        padding: [50, 60, 50, 60]
        
        Label:
            text: 'Hangman'
            font_size: 44
            size_hint_y: None
            height: 65
            color: 0.95, 0.95, 1.0, 1
            bold: True
        
        Label:
            text: 'Guess the word before the hangman is drawn!'
            font_size: 22
            size_hint_y: None
            height: 42
            color: 0.72, 0.72, 0.85, 1
        
        Widget:
            size_hint_y: 0.3
        
        StyledButton:
            text: 'Start Game'
            font_size: 34
            size_hint_y: None
            height: 85
            background_color: 0.7, 0.45, 0.25, 1
            on_press: root.manager.current = 'hm_game'
        
        Widget:
            size_hint_y: 0.3
        
        StyledButton:
            text: '← Back to Menu'
            font_size: 20
            size_hint_y: None
            height: 50
            background_color: 0.18, 0.18, 0.24, 1
            on_press: root.manager.current = 'menu'

<HangmanGameScreen>:
    canvas.before:
        Color:
            rgba: 0.04, 0.04, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 14
        padding: [28, 28, 28, 28]
        
        Label:
            id: word_display
            text: '_ _ _ _ _'
            font_size: 52
            size_hint_y: None
            height: 75
            color: 0.31, 0.8, 0.77, 1
            bold: True
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 40
            spacing: 25
            
            Label:
                id: wrong_guesses_label
                text: 'Wrong: '
                font_size: 22
                color: 1, 0.45, 0.45, 1
                text_size: self.size
                halign: 'left'
            
            Label:
                id: lives_label
                text: 'Lives: 6'
                font_size: 22
                color: 0.85, 0.9, 0.95, 1
                text_size: self.size
                halign: 'right'
        
        GridLayout:
            id: letter_grid
            cols: 7
            spacing: 10
            size_hint_y: 1
            padding: [12, 12, 12, 12]
        
        Label:
            id: status_message
            text: ''
            font_size: 20
            size_hint_y: None
            height: 35
            color: 0.9, 0.9, 0.98, 1
        
        StyledButton:
            text: '← Back to Menu'
            font_size: 20
            size_hint_y: None
            height: 50
            background_color: 0.18, 0.18, 0.24, 1
            on_press: root.manager.current = 'menu'         
""")

# Tic tac toe game logic
# All the ways you can win - these are the 8 possible lines on a 3x3 board
# Board positions are numbered 0-8 like this:
# 0 1 2
# 3 4 5
# 6 7 8
WIN_LINES = (
    (0, 1, 2),  # top row
    (3, 4, 5),  # middle row
    (6, 7, 8),  # bottom row
    (0, 3, 6),  # left column
    (1, 4, 7),  # middle column
    (2, 5, 8),  # right column
    (0, 4, 8),  # diagonal \
    (2, 4, 6),  # diagonal /
)

def check_winner(board):
    """Checks all the winning lines to see if someone won"""
    for a, b, c in WIN_LINES:
        # If all three positions have the same mark (and it's not empty), we have a winner
        if board[a] != "" and board[a] == board[b] == board[c]:
            return board[a]  # returns "X" or "O"
    return None  # nobody won yet

def is_draw(board):
    """Game is a draw if board is full and nobody won"""
    return all(cell != "" for cell in board) and check_winner(board) is None

def valid_moves(board):
    """Returns list of empty positions (indices) where a move can be made"""
    return [i for i, v in enumerate(board) if v == ""]

def minimax(board, player, ai, human):
    """
    Minimax algorithm - makes the AI play optimally
    Returns (score, best_move) where score is 1 for AI win, -1 for human win, 0 for draw
    """
    winner = check_winner(board)
    if winner == ai:
        return 1, None  # AI wins
    if winner == human:
        return -1, None  # Human wins
    if is_draw(board):
        return 0, None  # Draw

    moves = valid_moves(board)
    if player == ai:
        # AI wants the highest score possible
        best_score = -2
        best_move = None
        for m in moves:
            board[m] = ai
            score, _ = minimax(board, human, ai, human)
            board[m] = ""  # undo move after checking
            if score > best_score:
                best_score = score
                best_move = m
                if score == 1:  # found winning move, can stop searching
                    break
        return best_score, best_move
    else:
        # Human's turn - assume they'll make the best move for them (worst for AI)
        best_score = 2
        best_move = None
        for m in moves:
            board[m] = human
            score, _ = minimax(board, ai, ai, human)
            board[m] = ""  # undo move after checking
            if score < best_score:
                best_score = score
                best_move = m
                if score == -1:  # found move that blocks AI from winning
                    break
        return best_score, best_move

# Screen classes - each screen is a different page/view in the app
# The ScreenManager handles switching between these screens
class TitleScreen(Screen):
    """Welcome screen - first thing users see when app launches"""
    pass

class MenuScreen(Screen):
    """Main menu screen - shows all available games to choose from"""

    def show_under_development(self):
        layout = BoxLayout(orientation='vertical', spacing=15, padding=25)
        layout.add_widget(Label(text='Under Development', font_size=24, color=(0.95, 0.95, 1.0, 1)))
        btn = Button(
            text='OK',
            size_hint_y=None,
            height=50,
            font_size=20,
            bold=True,
            background_normal='',
            background_color=(0.85, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
        )
        layout.add_widget(btn)
        popup = Popup(
            title='Coming Soon',
            title_color=(0.95, 0.95, 1.0, 1),
            title_size=24,
            content=layout,
            size_hint=(0.5, 0.35),
            separator_color=(0.4, 0.4, 0.5, 1),
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

# Runs launch_robot.bat (Windows) or launch_robot.sh (Mac/Linux) in a new window
def launch_robot_script():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if sys.platform == 'win32':
        script_path = os.path.join(base_dir, 'launch_robot.bat')
        subprocess.Popen(
            [script_path],
            cwd=base_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    else:
        script_path = os.path.join(base_dir, 'launch_robot.sh')
        subprocess.Popen(['bash', script_path], cwd=base_dir)


class TicTacToeScreen(Screen):
    """Screen where you choose game mode before starting tic-tac-toe"""
    def start_game(self, vs_ai=False):
        self.manager.get_screen('ttt_game').vs_ai = vs_ai
        self.manager.current = 'ttt_game'


class TicTacToeDifficultyScreen(Screen):
    # Launches robot script, sets difficulty on game screen, then starts the game
    def start_with_difficulty(self, difficulty):
        launch_robot_script()
        game_screen = self.manager.get_screen('ttt_game')
        game_screen.vs_ai = True
        game_screen.difficulty = difficulty
        self.manager.current = 'ttt_game'

class TicTacToeGameScreen(Screen):
    """The actual game screen where you play tic tac toe"""
    
    def on_enter(self, *args):
        """Called every time we switch to this screen - resets everything"""
        self.current_player = "X"
        self.board_state = [""] * 9
        self.vs_ai = getattr(self, "vs_ai", False)
        self.difficulty = getattr(self, "difficulty", "impossible")  # easy, medium, hard, impossible
        self.human = "X"
        self.ai = "O"
        diff = self.difficulty.capitalize() if self.vs_ai else ""
        self.ids.status_label.text = f"Player X's Turn" + (f" (Difficulty: {diff})" if diff else "")
        self.draw_board()
        return super().on_enter(*args)
    
    def draw_board(self):
        """Creates all 9 buttons for the game board"""
        grid = self.ids.board
        grid.clear_widgets()
        
        for i in range(9):
            cell_value = self.board_state[i]
            if cell_value == "":
                bg_color = (0.1, 0.1, 0.15, 1)
                text_color = (0.5, 0.5, 0.6, 1)
            elif cell_value == "X":
                bg_color = (0.15, 0.5, 0.75, 1)
                text_color = (0.31, 0.8, 0.77, 1)
            else:
                bg_color = (0.7, 0.45, 0.2, 1)
                text_color = (1.0, 0.92, 0.55, 1)
            
            btn = Button(
                text=cell_value,
                font_size=52,
                background_normal='',
                background_color=bg_color,
                color=text_color,
                bold=True,
                on_press=lambda b, idx=i: self.make_move(idx, b),
            )
            grid.add_widget(btn)

    def make_move(self, index, button):
        """
        Handles a player making a move at a specific board position
        index: which cell was clicked (0-8)
        button: the actual button widget that was clicked
        """
        # Don't allow moves if cell is already taken or game already ended
        if self.board_state[index] != "" or check_winner(self.board_state):
            return
        
        # Place the current player's mark (X or O) on the board
        self.board_state[index] = self.current_player
        button.text = self.current_player  # Update the button to show X or O
        
        # Check if this move won the game
        winner = check_winner(self.board_state)
        if winner:
            self.show_popup(f"Player {winner} wins!")
            return
        elif is_draw(self.board_state):
            self.show_popup("It's a draw.")
            return
        
        self.current_player = "O" if self.current_player == "X" else "X"
        if self.vs_ai:
            # Show difficulty in status when playing vs robot
            diff = self.difficulty.capitalize()
            turn = "Your Turn" if self.current_player == self.human else "Robotic Arm's Turn"
            self.ids.status_label.text = f"{turn} (Difficulty: {diff})"
        else:
            self.ids.status_label.text = f"Player {self.current_player}'s Turn"
        
        # If playing against AI and it's now AI's turn, make the AI move automatically
        if self.vs_ai and self.current_player == self.ai:
            self.ai_move()
    
    def ai_move(self):
        # Pick move based on difficulty and play it
        move = self._get_ai_move()
        if move is not None:
            button = self.ids.board.children[8 - move]
            self.make_move(move, button)

    def _get_ai_move(self):
        # Easy: random. Medium: 30% optimal. Hard: 80% optimal. Impossible: minimax.
        moves = valid_moves(self.board_state)
        if not moves:
            return None

        diff = getattr(self, "difficulty", "impossible")

        if diff == "easy":
            return random.choice(moves)

        if diff == "medium":
            if random.random() < 0.3:
                move = self._try_win_or_block()
                if move is not None:
                    return move
            return random.choice(moves)

        if diff == "hard":
            if random.random() < 0.8:
                move = self._try_win_or_block()
                if move is not None:
                    return move
                _, move = minimax(self.board_state, self.ai, self.ai, self.human)
                if move is not None:
                    return move
            return random.choice(moves)

        # Impossible uses full minimax (unbeatable)
        _, move = minimax(self.board_state, self.ai, self.ai, self.human)
        return move if move is not None else random.choice(moves)

    def _try_win_or_block(self):
        # Try to win first, then block human from winning
        for move in valid_moves(self.board_state):
            self.board_state[move] = self.ai
            if check_winner(self.board_state) == self.ai:
                self.board_state[move] = ""
                return move
            self.board_state[move] = ""
        for move in valid_moves(self.board_state):
            self.board_state[move] = self.human
            if check_winner(self.board_state) == self.human:
                self.board_state[move] = ""
                return move
            self.board_state[move] = ""
        return None  # Make the move as if the button was clicked

    def show_popup(self, message):
        """Shows a popup with the game result"""
        layout = BoxLayout(orientation='vertical', spacing=20, padding=30)
        layout.add_widget(Label(
            text=message,
            font_size=24,
            color=(0.95, 0.95, 1.0, 1),
        ))
        btn = Button(
            text="Play Again",
            size_hint_y=None,
            height=55,
            font_size=22,
            bold=True,
            background_normal='',
            background_color=(0.2, 0.55, 0.8, 1),
            color=(1, 1, 1, 1),
        )
        layout.add_widget(btn)
        popup = Popup(
            title="Game Over",
            title_color=(0.95, 0.95, 1.0, 1),
            title_size=26,
            content=layout,
            size_hint=(0.65, 0.45),
            separator_color=(0.4, 0.4, 0.5, 1),
        )
        btn.bind(on_press=lambda *a: (popup.dismiss(), self.on_enter()))
        popup.open()
    


class HangmanScreen(Screen):
    """Hangman menu screen - shows before starting a game"""
    pass

class HangmanGameScreen(Screen):
    """
    Hangman gameplay screen - designed to be touch-friendly for robotic arm
    Players tap letter buttons to guess letters in the secret word
    """
    
    def on_enter(self, *args):
        """
        Called when this screen is shown - initializes a new game
        Picks a random word and resets all game state
        """
        # Pick a random word from our word list and convert to lowercase
        self.secret_word = random.choice(HANGMAN_WORDS).lower()
        # Sets to track which letters have been guessed correctly/incorrectly
        self.correct_guesses = set()  # Letters that are in the word
        self.wrong_guesses = set()    # Letters that are NOT in the word
        self.game_over = False
        
        # Update all the display elements
        self.update_word_display()      # Show word with underscores
        self.update_wrong_guesses()      # Show wrong letters (empty at start)
        self.update_lives()              # Show remaining lives (6 at start)
        self.ids.status_message.text = 'Tap a letter to guess!'
        
        # Create all the letter buttons (A-Z)
        self.create_letter_buttons()
        
        return super().on_enter(*args)
    
    def create_letter_buttons(self):
        """Creates touch-friendly letter buttons for A-Z"""
        grid = self.ids.letter_grid
        grid.clear_widgets()
        
        for letter in string.ascii_uppercase:
            btn = Button(
                text=letter,
                font_size=30,
                bold=True,
                background_normal='',
                background_color=(0.18, 0.4, 0.65, 1),
                color=(0.95, 0.95, 1.0, 1),
                on_press=lambda b, l=letter.lower(): self.guess_letter(l, b)
            )
            grid.add_widget(btn)
    
    def update_word_display(self):
        """
        Updates the word display to show guessed letters and underscores
        Example: if word is "python" and we guessed 'p' and 'o', shows "P _ _ _ O _"
        """
        display = " ".join(
            char if char in self.correct_guesses else "_"
            for char in self.secret_word
        )
        self.ids.word_display.text = display.upper()
    
    def update_wrong_guesses(self):
        """Updates the label showing which letters were guessed incorrectly"""
        if self.wrong_guesses:
            wrong_text = ', '.join(sorted(self.wrong_guesses))
            self.ids.wrong_guesses_label.text = f'Wrong: {wrong_text.upper()}'
        else:
            self.ids.wrong_guesses_label.text = 'Wrong: '
    
    def update_lives(self):
        """Updates the lives counter - shows how many wrong guesses you have left"""
        lives_left = MAX_MISSES - len(self.wrong_guesses)
        self.ids.lives_label.text = f'Lives: {lives_left}'
    
    def guess_letter(self, letter, button):
        """
        Handles when a player taps a letter button to make a guess
        letter: the letter that was guessed (lowercase)
        button: the button widget that was clicked
        """
        # Don't allow guesses if game is already over
        if self.game_over:
            return
        # Don't allow guessing the same letter twice
        if letter in self.correct_guesses or letter in self.wrong_guesses:
            self.ids.status_message.text = f"You already tried '{letter.upper()}'!"
            return
        
        # Check if the guessed letter is in the secret word
        if letter in self.secret_word:
            self.correct_guesses.add(letter)
            button.background_color = (0.2, 0.65, 0.45, 1)
            button.disabled = True  # Disable button so it can't be clicked again
            self.ids.status_message.text = f"Good guess! '{letter.upper()}' is in the word!"
            self.update_word_display()  # Update to show the letter in the word
            
            # Check if player won - all unique letters in the word have been guessed
            if all(char in self.correct_guesses for char in set(self.secret_word)):
                self.game_over = True
                self.show_popup(f"You won! The word was '{self.secret_word.upper()}'", won=True)
                return
        else:
            self.wrong_guesses.add(letter)
            button.background_color = (0.75, 0.25, 0.25, 1)
            button.disabled = True  # Disable button so it can't be clicked again
            self.ids.status_message.text = f"'{letter.upper()}' is not in the word."
            self.update_wrong_guesses()  # Update wrong guesses display
            self.update_lives()  # Update lives counter
            
            # Check if player lost - too many wrong guesses
            if len(self.wrong_guesses) >= MAX_MISSES:
                self.game_over = True
                self.show_popup(f"You lost! The word was '{self.secret_word.upper()}'", won=False)
                return
    
    def show_popup(self, message, won):
        """Shows a popup when the game ends (win or lose)"""
        layout = BoxLayout(orientation='vertical', spacing=22, padding=30)
        layout.add_widget(Label(text=message, font_size=22, color=(0.95, 0.95, 1.0, 1)))
        btn = Button(
            text="Play Again",
            size_hint_y=None,
            height=55,
            font_size=22,
            bold=True,
            background_normal='',
            background_color=(0.2, 0.55, 0.8, 1) if won else (0.65, 0.35, 0.25, 1),
            color=(1, 1, 1, 1),
        )
        layout.add_widget(btn)
        title = "You Won!" if won else "Game Over"
        popup = Popup(
            title=title,
            title_color=(0.95, 0.95, 1.0, 1),
            title_size=26,
            content=layout,
            size_hint=(0.7, 0.5),
            separator_color=(0.4, 0.4, 0.5, 1),
        )
        btn.bind(on_press=lambda *a: (popup.dismiss(), self.on_enter()))
        popup.open()

class MainApp(App):
    """Main application - Kivy runs this when the app starts"""
    
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        Window.fullscreen = True
        root = ScreenManager(transition=SlideTransition(duration=0.25))
        
        # Register all the screens with the screen manager
        # Each screen has a name that's used to switch between them
        root.add_widget(TitleScreen(name='title'))
        root.add_widget(MenuScreen(name='menu'))
        root.add_widget(TicTacToeScreen(name='ttt'))
        root.add_widget(TicTacToeDifficultyScreen(name='ttt_difficulty'))  # difficulty picker for vs robot
        root.add_widget(TicTacToeGameScreen(name='ttt_game'))
        root.add_widget(HangmanScreen(name='hm'))
        root.add_widget(HangmanGameScreen(name='hm_game'))
        
        return root

# Entry point - when you run this file, start the app
if __name__ == '__main__':
    MainApp().run()  # Create app instance and run it