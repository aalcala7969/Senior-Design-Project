from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen

# this can be put into a .kv file later
Builder.load_string("""
<TitleScreen>:
    BoxLayout:
        Button:
            text: 'Go to menu'
            on_press: root.manager.current = 'menu'
        Button:
            text: 'Quit'

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            Button:
                text: 'TicTacToe button'
                on_press: root.manager.current = 'ttt'
            Button:
                text: 'Hangman button'
                on_press: root.manager.current = 'hm'
            Button:
                text: 'Connect 4 button'
                on_press: root.manager.current = 'c4'
            Button:
                text: 'Dots and Boxes button'
                on_press: root.manager.current = 'dnb'
        Button:
            text: 'Back to title'
            on_press: root.manager.current = 'title'

<TicTacToeScreen>:
    BoxLayout:
        Label:
            text: 'Here is how to play...'
        Button:
            text: 'Play'
            on_press: root.manager.current = 'ttt_game'
        Button:
            text: 'Menu'
            on_press: root.manager.current = 'menu'

<TicTacToeGameScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'TicTacToeGame'
        GridLayout:
            id: 'tictactoe_board'
            rows: 3
            cols: 3
            Button:
                text: '0'                 
                on_press: root.get_move(0)   
            Button:
                text: '1'
                on_press: root.get_move(1)
            Button:
                text: '2'
                on_press: root.get_move(2)
            Button:
                text: '3'
                on_press: root.get_move(3)
            Button:
                text: '4'
                on_press: root.get_move(4)
            Button:
                text: '5'
                on_press: root.get_move(5)
            Button:
                text: '6'
                on_press: root.get_move(6)
            Button:
                text: '7'
                on_press: root.get_move(7)
            Button:
                text: '8'
                on_press: root.get_move(8)
        Button:
            text: 'Quit'
            on_press: root.manager.current = 'menu'         
""")


class TitleScreen(Screen):
    pass

class MenuScreen(Screen):
    pass

class TicTacToeScreen(Screen):
    pass

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