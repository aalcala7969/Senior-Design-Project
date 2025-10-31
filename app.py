from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout


# this can be put into a .kv file later
# KIVY LAYOUT
Builder.load_string("""
<TitleScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 40
        Button:
            text: 'Go to menu'
            on_press: root.manager.current = 'menu'
        Button:
            text: 'Quit'
            on_press: app.stop()

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 40
        BoxLayout:
            orientation: 'horizontal'
            spacing: 10
            Button:
                text: 'Play TicTacToe'
                on_press: root.manager.current = 'ttt'
            Button:
                text: 'Hangman (WIP)'
                on_press: root.manager.current = 'hm'
            Button:
                text: 'Connect 4 (WIP)'
                on_press: root.manager.current = 'c4'
            Button:
                text: 'Dots and Boxes (WIP)'
                on_press: root.manager.current = 'dnb'
        Button:
            text: 'Back to title'
            on_press: root.manager.current = 'title'

<TicTacToeScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 40
        Label:
            text: 'Here is how to play...'
        Label:
            text: 'Choose mode' 
        Button:
            text: 'Two Players'
            on_press: root.start_game(vs_ai=False)
        Button:
            text: 'Play vs CPU'
            on_press: root.start_game(vs_ai=True)
        Button:
            text: 'Menu'
            on_press: root.manager.current = 'menu'

<TicTacToeGameScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 20
        Label:
            id: status_label
            text: "Player X's Turn"
            size_hint_y: None
            height: 40
        GridLayout:
            id: board
            rows: 3
            cols: 3
            spacing: 5
        Button:
            text: 'Back to Menu'
            size_hint_y: None
            height: 40
            on_press: root.manager.current = 'menu'         
""")

# TicTacToe Game Logic
WIN_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)

def check_winner(board):
    for a, b, c in WIN_LINES:
        if board[a] != "" and board[a] == board[b] == board[c]:
            return board[a]
    return None

def is_draw(board):
    return all(cell != "" for cell in board) and check_winner(board) is None

def valid_moves(board):
    return [i for i, v in enumerate(board) if v == ""]

def minimax(board, player, ai, human):
    winner = check_winner(board)
    if winner == ai:
        return 1, None
    if winner == human:
        return -1, None
    if is_draw(board):
        return 0, None

    moves = valid_moves(board)
    if player == ai:
        best_score = -2
        best_move = None
        for m in moves:
            board[m] = ai
            score, _ = minimax(board, human, ai, human)
            board[m] = ""
            if score > best_score:
                best_score = score
                best_move = m
                if score == 1:
                    break
        return best_score, best_move
    else:
        best_score = 2
        best_move = None
        for m in moves:
            board[m] = human
            score, _ = minimax(board, ai, ai, human)
            board[m] = ""
            if score < best_score:
                best_score = score
                best_move = m
                if score == -1:
                    break
        return best_score, best_move

# Kivy Screens
class TitleScreen(Screen):
    pass

class MenuScreen(Screen):
    pass

class TicTacToeScreen(Screen):
    def start_game(self, vs_ai=False):
        self.manager.get_screen('ttt_game').vs_ai = vs_ai
        self.manager.current = 'ttt_game'

class TicTacToeGameScreen(Screen):
    def on_enter(self, *args):
        self.current_player = "X"
        self.board_state = [""] * 9
        self.vs_ai = getattr(self, "vs_ai", False)
        self.human = "X"
        self.ai = "O"
        self.ids.status_label.text = "Player X's Turn"
        self.draw_board()
        return super().on_enter(*args)
    
    #tictactoe button widgets dynamically created
    def draw_board(self):
        grid = self.ids.board
        grid.clear_widgets()
        for i in range(9):
            btn = Button(
                text=self.board_state[i],
                font_size=48,
                on_press=lambda b, idx=i: self.make_move(idx, b),
            )
            grid.add_widget(btn)

    def make_move(self, index, button):
        # invalid move or game is already won
        if self.board_state[index] != "" or check_winner(self.board_state):
            return
        # update board state and GUI to match
        self.board_state[index] = self.current_player
        button.text = self.current_player
        # check if move results in a win
        winner = check_winner(self.board_state)
        if winner:
            return
        elif is_draw(self.board_state):
            return
        
        # switch turns 
        self.current_player = "O" if self.current_player == "X" else "X"
        self.ids.status_label.text = f"Player {self.current_player}'s Turn"
    


class HangmanScreen(Screen):
    pass

class HangmanGameScreen(Screen):
    pass

class MainApp(App):
    def build(self):
        root = ScreenManager()
        root.add_widget(TitleScreen(name='title'))
        root.add_widget(MenuScreen(name='menu'))
        root.add_widget(TicTacToeScreen(name='ttt'))
        root.add_widget(TicTacToeGameScreen(name='ttt_game'))
        root.add_widget(HangmanScreen(name='hm'))
        root.add_widget(HangmanGameScreen(name='hm_game'))
        return root

MainApp().run()