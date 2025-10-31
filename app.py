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
            text: 'Player Xs Turn'
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
        self.func()
        return super().on_enter(*args)
    # TODO: implement tictactoe button functions here
    def func(self):
        print("i'm here")
    def get_move(self, choice: int):
        print(choice)
    pass

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