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
from kivy.uix.button import Button  # Clickable buttons
from kivy.uix.popup import Popup  # Popup windows
from kivy.uix.label import Label  # Text labels
from kivy.uix.boxlayout import BoxLayout  # Container that arranges widgets in a line
from kivy.uix.gridlayout import GridLayout  # Container that arranges widgets in a grid
import random  # For random word selection and AI moves
import string  # For getting all letters A-Z

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
<TitleScreen>:
    # Background color for the welcome screen
    canvas.before:
        Color:
            rgba: 0.15, 0.15, 0.25, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 30
        padding: [50, 80, 50, 80]
        
        # Main title at the top
        Label:
            text: 'Robotic Gaming Arm'
            font_size: 56
            size_hint_y: None
            height: 80
            color: 0.9, 0.9, 0.95, 1
            bold: True
        
        # Subtitle text
        Label:
            text: 'We hope you enjoy!'
            font_size: 24
            size_hint_y: None
            height: 50
            color: 0.75, 0.75, 0.85, 1
        
        # Empty space to push buttons down
        Widget:
            size_hint_y: 1
        
        # Main action buttons - made these bigger so they're easier to click
        Button:
            text: "Let's Play!"
            font_size: 36
            size_hint_y: None
            height: 90
            background_color: 0.2, 0.6, 0.8, 1
            on_press: root.manager.current = 'menu'  # switches to menu screen
        
        Button:
            text: 'Maybe Later'
            font_size: 26
            size_hint_y: None
            height: 70
            background_color: 0.4, 0.4, 0.5, 1
            on_press: app.stop()  # closes the app

<MenuScreen>:
    canvas.before:
        Color:
            rgba: 0.12, 0.12, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 25
        padding: [40, 50, 40, 50]
        
        # Menu title
        Label:
            text: 'What would you like to play?'
            font_size: 32
            size_hint_y: None
            height: 60
            color: 0.9, 0.9, 0.95, 1
            bold: True
        
        # Game buttons in a 2x2 grid
        GridLayout:
            cols: 2
            spacing: 15
            size_hint_y: 1
            padding: [0, 20, 0, 20]
            
            Button:
                text: 'Tic Tac Toe'
                font_size: 22
                background_color: 0.25, 0.65, 0.85, 1
                on_press: root.manager.current = 'ttt'  # goes to tic tac toe screen
            
            Button:
                text: 'Hangman'
                font_size: 22
                background_color: 0.7, 0.5, 0.3, 1
                on_press: root.manager.current = 'hm'  # hangman screen (not implemented yet)
            
            Button:
                text: 'Connect 4'
                font_size: 22
                background_color: 0.6, 0.4, 0.7, 1
                on_press: root.manager.current = 'c4'  # connect 4 screen (not implemented yet)
            
            Button:
                text: 'Dots & Boxes'
                font_size: 22
                background_color: 0.5, 0.7, 0.5, 1
                on_press: root.manager.current = 'dnb'  # dots and boxes (not implemented yet)
        
        # Back button
        Button:
            text: '← Back'
            font_size: 18
            size_hint_y: None
            height: 45
            background_color: 0.35, 0.35, 0.45, 1
            on_press: root.manager.current = 'title'

<TicTacToeScreen>:
    canvas.before:
        Color:
            rgba: 0.12, 0.12, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 20
        padding: [50, 60, 50, 60]
        
        # Game title
        Label:
            text: 'Tic Tac Toe'
            font_size: 42
            size_hint_y: None
            height: 70
            color: 0.9, 0.9, 0.95, 1
            bold: True
        
        # Instructions
        Label:
            text: 'Get three in a row to win!'
            font_size: 20
            size_hint_y: None
            height: 40
            color: 0.7, 0.7, 0.8, 1
        
        # Spacer
        Widget:
            size_hint_y: 0.3
        
        # Mode selection
        Label:
            text: 'Choose your game mode:'
            font_size: 22
            size_hint_y: None
            height: 45
            color: 0.8, 0.8, 0.9, 1
        
        Button:
            text: 'Two Players'
            font_size: 24
            size_hint_y: None
            height: 65
            background_color: 0.3, 0.7, 0.5, 1
            on_press: root.start_game(vs_ai=False)
        
        Button:
            text: 'Play vs CPU'
            font_size: 24
            size_hint_y: None
            height: 65
            background_color: 0.25, 0.65, 0.85, 1
            on_press: root.start_game(vs_ai=True)
        
        # Spacer
        Widget:
            size_hint_y: 0.3
        
        # Back button
        Button:
            text: '← Back to Menu'
            font_size: 18
            size_hint_y: None
            height: 45
            background_color: 0.35, 0.35, 0.45, 1
            on_press: root.manager.current = 'menu'

<TicTacToeGameScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.18, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 20
        padding: [30, 40, 30, 30]
        
        # Status display - shows whose turn it is
        Label:
            id: status_label
            text: "Player X's Turn"
            font_size: 26
            size_hint_y: None
            height: 50
            color: 0.9, 0.9, 0.95, 1
            bold: True
        
        # Game board - 3x3 grid for tic tac toe
        GridLayout:
            id: board
            rows: 3
            cols: 3
            spacing: 8
            size_hint_y: 1
            padding: [20, 20, 20, 20]
        
        # Navigation button
        Button:
            text: '← Back to Menu'
            font_size: 18
            size_hint_y: None
            height: 45
            background_color: 0.35, 0.35, 0.45, 1
            on_press: root.manager.current = 'menu'

<HangmanScreen>:
    canvas.before:
        Color:
            rgba: 0.12, 0.12, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 20
        padding: [50, 60, 50, 60]
        
        Label:
            text: 'Hangman'
            font_size: 42
            size_hint_y: None
            height: 70
            color: 0.9, 0.9, 0.95, 1
            bold: True
        
        Label:
            text: 'Guess the word before the hangman is drawn!'
            font_size: 20
            size_hint_y: None
            height: 40
            color: 0.7, 0.7, 0.8, 1
        
        Widget:
            size_hint_y: 0.3
        
        Button:
            text: 'Start Game'
            font_size: 32
            size_hint_y: None
            height: 80
            background_color: 0.7, 0.5, 0.3, 1
            on_press: root.manager.current = 'hm_game'
        
        Widget:
            size_hint_y: 0.3
        
        Button:
            text: '← Back to Menu'
            font_size: 18
            size_hint_y: None
            height: 45
            background_color: 0.35, 0.35, 0.45, 1
            on_press: root.manager.current = 'menu'

<HangmanGameScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.18, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: [20, 20, 20, 20]
        
        # Word display
        Label:
            id: word_display
            text: '_ _ _ _ _'
            font_size: 48
            size_hint_y: None
            height: 70
            color: 0.9, 0.9, 0.95, 1
            bold: True
        
        # Wrong guesses and lives in a horizontal layout
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 35
            spacing: 20
            
            Label:
                id: wrong_guesses_label
                text: 'Wrong: '
                font_size: 20
                color: 1, 0.5, 0.5, 1
                text_size: self.size
                halign: 'left'
            
            Label:
                id: lives_label
                text: 'Lives: 6'
                font_size: 20
                color: 0.8, 0.8, 0.9, 1
                text_size: self.size
                halign: 'right'
        
        # Letter buttons grid - full width, touch-friendly
        GridLayout:
            id: letter_grid
            cols: 7
            spacing: 8
            size_hint_y: 1
            padding: [10, 10, 10, 10]
        
        # Status message
        Label:
            id: status_message
            text: ''
            font_size: 18
            size_hint_y: None
            height: 30
            color: 0.9, 0.9, 0.95, 1
        
        # Back button
        Button:
            text: '← Back to Menu'
            font_size: 18
            size_hint_y: None
            height: 40
            background_color: 0.35, 0.35, 0.45, 1
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
    pass

class TicTacToeScreen(Screen):
    """Screen where you choose game mode before starting tic-tac-toe"""
    def start_game(self, vs_ai=False):
        # Get the game screen and set whether we're playing against AI
        # vs_ai=True means play against computer, vs_ai=False means 2 players
        self.manager.get_screen('ttt_game').vs_ai = vs_ai
        self.manager.current = 'ttt_game'  # Switch to the actual game screen

class TicTacToeGameScreen(Screen):
    """The actual game screen where you play tic tac toe"""
    
    def on_enter(self, *args):
        """Called every time we switch to this screen - resets everything"""
        self.current_player = "X"  # X always goes first
        self.board_state = [""] * 9  # empty board with 9 cells
        self.vs_ai = getattr(self, "vs_ai", False)  # check if we're playing AI
        self.human = "X"
        self.ai = "O"
        self.ids.status_label.text = "Player X's Turn"
        self.draw_board()  # create the board buttons
        return super().on_enter(*args)
    
    def draw_board(self):
        """Creates all 9 buttons for the game board"""
        grid = self.ids.board
        grid.clear_widgets()  # remove old buttons if any
        
        for i in range(9):
            cell_value = self.board_state[i]
            # Different colors for empty cells vs X vs O
            if cell_value == "":
                bg_color = (0.2, 0.2, 0.3, 1)  # dark gray for empty
                text_color = (0.6, 0.6, 0.7, 1)
            elif cell_value == "X":
                bg_color = (0.2, 0.4, 0.6, 1)  # blue-ish for X
                text_color = (0.9, 0.95, 1.0, 1)
            else:  # O
                bg_color = (0.6, 0.4, 0.2, 1)  # orange-ish for O
                text_color = (1.0, 0.95, 0.9, 1)
            
            btn = Button(
                text=cell_value,
                font_size=48,
                background_color=bg_color,
                color=text_color,
                bold=True,
                on_press=lambda b, idx=i: self.make_move(idx, b),  # lambda to capture the index
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
        
        # Switch to the other player's turn
        self.current_player = "O" if self.current_player == "X" else "X"
        self.ids.status_label.text = f"Player {self.current_player}'s Turn"
        
        # If playing against AI and it's now AI's turn, make the AI move automatically
        if self.vs_ai and self.current_player == self.ai:
            self.ai_move()
    
    def ai_move(self):
        """
        Makes the AI's move using the minimax algorithm
        The minimax function returns (score, best_move) - we only need the move
        """
        _, move = minimax(self.board_state, self.ai, self.ai, self.human)
        # Fallback: if minimax somehow returns None, pick a random valid move
        if move is None:
            moves = valid_moves(self.board_state)
            move = random.choice(moves) if moves else None
        
        if move is not None:
            # GridLayout stores children in reverse order, so we need to flip the index
            # If move is 0, we want the 8th child (last one), etc.
            button = self.ids.board.children[8 - move] 
            self.make_move(move, button)  # Make the move as if the button was clicked

    def show_popup(self, message):
        """Shows a popup with the game result"""
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        layout.add_widget(Label(text=message, font_size=20))
        btn = Button(text="Play Again", size_hint_y=None, height=40)
        layout.add_widget(btn)
        popup = Popup(title="Game Over", content=layout, size_hint=(0.6, 0.4))
        # When they click "Play Again", close popup and reset the game
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
        """
        Creates a button for each letter A-Z
        These buttons are large and touch-friendly for robotic arm interaction
        """
        grid = self.ids.letter_grid
        grid.clear_widgets()  # Clear any existing buttons
        
        # Create a button for each letter in the alphabet
        for letter in string.ascii_uppercase:
            btn = Button(
                text=letter,  # Show the letter on the button
                font_size=32,  # Large font size for easy tapping
                background_color=(0.3, 0.5, 0.7, 1),  # Blue color
                # When clicked, call guess_letter with the lowercase version
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
            # Correct guess!
            self.correct_guesses.add(letter)
            button.background_color = (0.2, 0.7, 0.3, 1)  # Turn button green
            button.disabled = True  # Disable button so it can't be clicked again
            self.ids.status_message.text = f"Good guess! '{letter.upper()}' is in the word!"
            self.update_word_display()  # Update to show the letter in the word
            
            # Check if player won - all unique letters in the word have been guessed
            if all(char in self.correct_guesses for char in set(self.secret_word)):
                self.game_over = True
                self.show_popup(f"You won! The word was '{self.secret_word.upper()}'", won=True)
                return
        else:
            # Wrong guess!
            self.wrong_guesses.add(letter)
            button.background_color = (0.7, 0.2, 0.2, 1)  # Turn button red
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
        """
        Shows a popup window when the game ends (win or lose)
        message: the message to display
        won: True if player won, False if player lost
        """
        # Create a vertical layout for the popup content
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        layout.add_widget(Label(text=message, font_size=20))
        btn = Button(text="Play Again", size_hint_y=None, height=50, font_size=20)
        layout.add_widget(btn)
        
        # Set popup title based on win/lose
        title = "You Won!" if won else "Game Over"
        popup = Popup(title=title, content=layout, size_hint=(0.7, 0.5))
        
        # When "Play Again" is clicked, close popup and reset the game
        btn.bind(on_press=lambda *a: (popup.dismiss(), self.on_enter()))
        popup.open()

class MainApp(App):
    """
    Main application class - this is what Kivy runs when the app starts
    The build() method is called by Kivy to create the app's UI
    """
    def build(self):
        """
        Creates and returns the root widget (ScreenManager)
        The ScreenManager handles switching between different screens
        """
        root = ScreenManager()
        
        # Register all the screens with the screen manager
        # Each screen has a name that's used to switch between them
        root.add_widget(TitleScreen(name='title'))          # Welcome screen
        root.add_widget(MenuScreen(name='menu'))            # Game selection menu
        root.add_widget(TicTacToeScreen(name='ttt'))        # Tic-tac-toe mode selection
        root.add_widget(TicTacToeGameScreen(name='ttt_game')) # Tic-tac-toe gameplay
        root.add_widget(HangmanScreen(name='hm'))           # Hangman menu
        root.add_widget(HangmanGameScreen(name='hm_game'))  # Hangman gameplay
        
        return root  # Return the ScreenManager as the root widget

# Entry point - when you run this file, start the app
if __name__ == '__main__':
    MainApp().run()  # Create app instance and run it