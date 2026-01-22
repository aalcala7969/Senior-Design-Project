from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
import random

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

# Screen classes - each screen is a different page in the app
class TitleScreen(Screen):
    """First screen you see when the app starts"""
    pass

class MenuScreen(Screen):
    """Main menu where you pick which game to play"""
    pass

class TicTacToeScreen(Screen):
    """Screen where you choose 2-player or vs AI mode"""
    def start_game(self, vs_ai=False):
        # Tell the game screen whether we're playing against AI or not
        self.manager.get_screen('ttt_game').vs_ai = vs_ai
        self.manager.current = 'ttt_game'  # switch to the game screen

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
        """Called when someone clicks a cell on the board"""
        # Don't allow moves if cell is taken or game already ended
        if self.board_state[index] != "" or check_winner(self.board_state):
            return
        
        # Update the board state and button display
        self.board_state[index] = self.current_player
        button.text = self.current_player
        
        # Check if someone won
        winner = check_winner(self.board_state)
        if winner:
            self.show_popup(f"Player {winner} wins!")
            return
        elif is_draw(self.board_state):
            self.show_popup("It's a draw.")
            return
        
        # Switch turns
        self.current_player = "O" if self.current_player == "X" else "X"
        self.ids.status_label.text = f"Player {self.current_player}'s Turn"
        
        # If it's AI's turn, make the AI move automatically
        if self.vs_ai and self.current_player == self.ai:
            self.ai_move()
    
    def ai_move(self):
        """AI picks its move using minimax, then makes it"""
        _, move = minimax(self.board_state, self.ai, self.ai, self.human)
        # Just in case minimax returns None (shouldn't happen but you never know)
        if move is None:
            moves = valid_moves(self.board_state)
            move = random.choice(moves) if moves else None
        
        if move is not None:
            # GridLayout stores children in reverse order, so need to flip the index
            button = self.ids.board.children[8 - move] 
            self.make_move(move, button)  # make the move as if the button was clicked

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
    """Hangman game screen - not implemented yet"""
    pass

class HangmanGameScreen(Screen):
    """Hangman gameplay screen - not implemented yet"""
    pass

class MainApp(App):
    """Main app class - this is what Kivy runs"""
    def build(self):
        root = ScreenManager()
        # Register all the screens with the screen manager
        root.add_widget(TitleScreen(name='title'))
        root.add_widget(MenuScreen(name='menu'))
        root.add_widget(TicTacToeScreen(name='ttt'))
        root.add_widget(TicTacToeGameScreen(name='ttt_game'))
        root.add_widget(HangmanScreen(name='hm'))
        root.add_widget(HangmanGameScreen(name='hm_game'))
        return root

# Run the app
if __name__ == '__main__':
    MainApp().run()