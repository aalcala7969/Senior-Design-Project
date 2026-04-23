"""
Robotic Gaming Arm - GUI Launcher
Strictly used as a lightweight boot menu. 
Once a game is selected, this app terminates to free RAM for YOLOv5/ROS.
"""
import os

# CRITICAL FIX: Force the 1080p resolution and fullscreen BEFORE Kivy builds the window
from kivy.config import Config
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')
Config.set('graphics', 'fullscreen', 'auto')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window

# ... [Keep your existing Builder.load_string code here] ...


Builder.load_string("""
<StyledButton@Button>:
    background_normal: ''
    background_color: 0.15, 0.15, 0.2, 1
    color: 0.95, 0.95, 1.0, 1
    font_size: 33
    bold: True
    border: (0, 0, 0, 0)

<CardButton@Button>:
    background_normal: ''
    background_color: 0.12, 0.12, 0.18, 1
    color: 0.95, 0.95, 1.0, 1
    font_size: 36
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
            
    # AnchorLayout forces its children into the absolute center
    AnchorLayout:
        anchor_x: 'center'
        anchor_y: 'center'
        
        # This box takes up exactly 60% of the screen width and 70% of the height
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.6, 0.7
            spacing: 42
            
            Label:
                text: 'RGA'
                font_size: 144
                size_hint_y: None
                height: 160
                color: 0.95, 0.32, 0.32, 1
                bold: True
            Label:
                text: 'Robotic Gaming Arm'
                font_size: 48
                size_hint_y: None
                height: 72
            
            Widget:
                size_hint_y: 0.1
                
            StyledButton:
                text: "Let's Play!"
                font_size: 72
                size_hint_y: None
                height: 165
                background_color: 0.15, 0.52, 0.82, 1
                on_press: root.manager.current = 'menu'
            StyledButton:
                text: 'Sleep'
                font_size: 39
                size_hint_y: None
                height: 96
                background_color: 0.22, 0.24, 0.32, 1
                on_press: app.stop()

<MenuScreen>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
            
    AnchorLayout:
        anchor_x: 'center'
        anchor_y: 'center'
        
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.6, 0.7
            spacing: 30
            
            Label:
                text: 'Choose Game'
                font_size: 72
                size_hint_y: None
                height: 120
                color: 0.95, 0.95, 1.0, 1
                bold: True
                
            GridLayout:
                cols: 2
                spacing: 24
                size_hint_y: None
                height: 150
                CardButton:
                    text: 'Tic Tac Toe'
                    background_color: 0.12, 0.3, 0.38, 1
                    on_press: root.manager.current = 'ttt'
                CardButton:
                    text: 'Hangman'
                    background_color: 0.1, 0.35, 0.35, 1
                    on_press: root.manager.current = 'hm'
                    
            Widget:
                size_hint_y: 0.2
                
            StyledButton:
                text: '← Back'
                font_size: 30
                size_hint_y: None
                height: 75
                background_color: 0.85, 0.2, 0.2, 1
                on_press: root.manager.current = 'title'

<TicTacToeScreen>:
    canvas.before:
        Color:
            rgba: 0.04, 0.04, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size
            
    AnchorLayout:
        anchor_x: 'center'
        anchor_y: 'center'
        
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.6, 0.7
            spacing: 36
            
            Label:
                text: 'Tic Tac Toe'
                font_size: 66
                size_hint_y: None
                height: 90
                bold: True
            Label:
                text: 'Select Difficulty'
                font_size: 36
                size_hint_y: None
                height: 60
                
            StyledButton:
                text: 'Easy'
                size_hint_y: None
                height: 97
                background_color: 0.25, 0.65, 0.45, 1
                on_press: root.start_with_difficulty('easy')
            StyledButton:
                text: 'Hard'
                size_hint_y: None
                height: 97
                background_color: 0.85, 0.2, 0.2, 1
                on_press: root.start_with_difficulty('hard')
                
            Widget:
                size_hint_y: 0.2
                
            StyledButton:
                text: '← Back to Menu'
                font_size: 30
                size_hint_y: None
                height: 75
                background_color: 0.18, 0.18, 0.24, 1
                on_press: root.manager.current = 'menu'

<HangmanScreen>:
    canvas.before:
        Color:
            rgba: 0.04, 0.04, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size
            
    AnchorLayout:
        anchor_x: 'center'
        anchor_y: 'center'
        
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.6, 0.7
            spacing: 42
            
            Label:
                text: 'Hangman'
                font_size: 66
                size_hint_y: None
                height: 90
                bold: True
                
            Widget:
                size_hint_y: 0.3
                
            StyledButton:
                text: 'Start Game'
                font_size: 51
                size_hint_y: None
                height: 127
                background_color: 0.7, 0.45, 0.25, 1
                on_press: root.start_hangman()
                
            Widget:
                size_hint_y: 0.3
                
            StyledButton:
                text: '← Back to Menu'
                font_size: 30
                size_hint_y: None
                height: 75
                background_color: 0.18, 0.18, 0.24, 1
                on_press: root.manager.current = 'menu'
""")

class TitleScreen(Screen): pass
class MenuScreen(Screen): pass

class TicTacToeScreen(Screen):
    def start_with_difficulty(self, difficulty):
        with open('/tmp/vrom_game_request.txt', 'w') as f:
            f.write(f"tictactoe,{difficulty}")

class HangmanScreen(Screen):
    def start_hangman(self):
        with open('/tmp/vrom_game_request.txt', 'w') as f:
            f.write("hangman,normal")

class MainApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        root = ScreenManager(transition=SlideTransition(duration=0.25))
        root.add_widget(TitleScreen(name='title'))
        root.add_widget(MenuScreen(name='menu'))
        root.add_widget(TicTacToeScreen(name='ttt'))
        root.add_widget(HangmanScreen(name='hm'))
        return root

if __name__ == '__main__':
    MainApp().run()
