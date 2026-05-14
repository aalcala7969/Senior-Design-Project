"""
Robotic Gaming Arm - GUI Launcher
Strictly used as a lightweight boot menu. 
Once a game is selected, this app terminates to free RAM for YOLOv5/ROS.
"""
import os
import threading
import subprocess

os.environ['KIVY_CAMERA'] = '' # Stops Kivy from locking /dev/video0
os.environ['KIVY_VIDEO'] = ''

# CRITICAL FIX: Force the 1080p resolution and fullscreen BEFORE Kivy builds the window
from kivy.config import Config
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')
Config.set('graphics', 'fullscreen', 'auto')
# Hide the default multitouch-emulation red dot (right-click / ctrl+click)
try:
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
except Exception:
    pass

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty


#:import dp kivy.metrics.dp
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

<OverlayPickButton@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0.5
    color: 1, 1, 1, 1
    font_size: 36
    bold: True
    halign: 'center'
    valign: 'bottom'
    padding_y: 16

<TitleScreen>:
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
            size_hint: 0.99, 0.99
            spacing: 2
            padding: 8, 2, 8, 4
            Label:
                text: 'Welcome to'
                font_size: 84
                size_hint_y: None
                height: 96
                color: 0.9, 0.9, 0.95, 1
                bold: True
            # RGA centered on the full hero; sponsor panel placed just to the right of the mark (not screen corner)
            FloatLayout:
                id: rga_hero_frame
                size_hint: 1, 1
                Image:
                    id: rga_hero
                    source: app.rga_logo
                    size_hint: 0.84, 0.995
                    pos_hint: {'center_x': 0.5, 'y': 0.005}
                    allow_stretch: True
                    keep_ratio: True
                    opacity: 1 if app.rga_uses_file else 0
                Label:
                    id: rga_fallback
                    text: 'RGA' if not app.rga_uses_file else ''
                    font_size: 200
                    size_hint: 0.84, 0.92
                    pos_hint: {'center_x': 0.5, 'y': 0.015}
                    text_size: self.size
                    halign: 'center'
                    valign: 'bottom'
                    color: 0.95, 0.32, 0.32, 1
                    bold: True
            BoxLayout:
                orientation: 'vertical'
                size_hint: 1, None
                height: 361
                spacing: 6
                padding: 0, 0, 0, 0
                StyledButton:
                    text: "Let's Play!"
                    font_size: 93
                    size_hint_y: None
                    height: 273
                    background_color: 0.15, 0.52, 0.82, 1
                    on_release: root.manager.current = 'menu'
                StyledButton:
                    text: 'Sleep'
                    font_size: 32
                    size_hint_y: None
                    height: 82
                    background_color: 0.22, 0.24, 0.32, 1
                    on_release: app.shutdown_system()

<MenuScreen>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    FloatLayout:
        # Game picker: two image tiles
        BoxLayout:
            id: pick_layer
            orientation: 'vertical'
            size_hint: 1, 1
            pos: 0, 0
            padding: 18
            spacing: 16
            Label:
                text: 'Choose Game'
                font_size: 140
                size_hint_y: None
                height: 200
                color: 0.95, 0.95, 1.0, 1
                bold: True
            Label:
                text: 'What game would you like to play against the robot?'
                font_size: 52
                size_hint_y: None
                height: 80
                color: 0.65, 0.65, 0.75, 1
            GridLayout:
                cols: 2
                spacing: 20
                size_hint_y: 0.75
                RelativeLayout:
                    Image:
                        source: app.tictactoe_image
                        size_hint: 1, 1
                        pos: 0, 0
                        allow_stretch: True
                        keep_ratio: True
                    OverlayPickButton:
                        size_hint: 1, 1
                        text: 'Tic Tac Toe\\nTap to select'
                        on_release: root.open_game('ttt')
                RelativeLayout:
                    Image:
                        source: app.hangman_image
                        size_hint: 1, 1
                        pos: 0, 0
                        allow_stretch: True
                        keep_ratio: True
                    OverlayPickButton:
                        size_hint: 1, 1
                        text: 'Hangman\\nTap to select'
                        on_release: root.open_game('hm')
            StyledButton:
                text: '← Back to Welcome'
                font_size: 28
                size_hint_y: None
                height: 80
                background_color: 0.85, 0.2, 0.2, 1
                on_release: root.manager.current = 'title'
        # Detail: Tic Tac Toe
        BoxLayout:
            id: ttt_layer
            orientation: 'vertical'
            size_hint: 0, 0
            pos: 0, 0
            padding: 20
            spacing: 12
            disabled: True
            opacity: 0
            # Two-column layout filling the screen
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: 1
                spacing: 20
                # Left column: title top-left, buttons bottom-left
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: 0.5
                    spacing: 16
                    Label:
                        text: 'Tic Tac Toe'
                        font_size: 110
                        size_hint_y: 0.42
                        text_size: (self.width, self.height)
                        halign: 'center'
                        valign: 'middle'
                        color: 1, 1, 1, 1
                        bold: True
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: 0.58
                        spacing: 18
                        padding: 0, 0, 0, 0
                        StyledButton:
                            text: 'Easy\\nLess Optimized for Higher Win Rate'
                            font_size: 40
                            size_hint_y: 1
                            halign: 'center'
                            valign: 'middle'
                            text_size: self.size
                            background_color: 0.2, 0.62, 0.45, 1
                            on_release: root.choose_ttt_difficulty('easy')
                        StyledButton:
                            text: 'Hard\\nUnbeatable'
                            font_size: 40
                            size_hint_y: 1
                            halign: 'center'
                            valign: 'middle'
                            text_size: self.size
                            background_color: 0.82, 0.18, 0.22, 1
                            on_release: root.choose_ttt_difficulty('hard')
                        StyledButton:
                            text: '← Back to game list'
                            font_size: 28
                            size_hint_y: None
                            height: 80
                            background_color: 0.18, 0.18, 0.26, 1
                            on_release: root.close_game()
                # Right column: image top-right, description bottom-right
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: 0.5
                    spacing: 16
                    Image:
                        source: app.tictactoe_image
                        size_hint_y: 0.5
                        allow_stretch: True
                        keep_ratio: True
                    Label:
                        text: "Play on a 3x3 board. Get three in a row before the robot does. This game utilizes the Minimax algorithm to predict the best move to make against the human user. The robot will draw the game board when selected. Our trained YOLOv5 model was created to detect the state of the game map. When the robot makes it's move, it will give the user 5 seconds before doing an iterative scan of the game map. Look for information on the screen while playing this game!"
                        font_size: 38
                        size_hint_y: 0.5
                        text_size: (self.width - 20, self.height - 20)
                        halign: 'center'
                        valign: 'top'
                        color: 0.82, 0.82, 0.94, 1
        # Detail: Hangman
        BoxLayout:
            id: hm_layer
            orientation: 'vertical'
            size_hint: 0, 0
            pos: 0, 0
            padding: 20
            spacing: 12
            disabled: True
            opacity: 0
            # Two-column layout filling the screen
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: 1
                spacing: 20
                # Left column: title top-left, buttons bottom-left
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: 0.5
                    spacing: 16
                    Label:
                        text: 'Hangman'
                        font_size: 110
                        size_hint_y: 0.42
                        text_size: (self.width, self.height)
                        halign: 'center'
                        valign: 'middle'
                        color: 1, 1, 1, 1
                        bold: True
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: 0.58
                        spacing: 18
                        padding: 0, 0, 0, 0
                        StyledButton:
                            text: 'Standard\\nNOT AVAILABLE'
                            font_size: 38
                            size_hint_y: 1
                            halign: 'center'
                            valign: 'middle'
                            text_size: self.size
                            background_color: 0.68, 0.42, 0.2, 1
                            on_release: root.start_hangman()
                        StyledButton:
                            text: '← Back to game list'
                            font_size: 28
                            size_hint_y: None
                            height: 80
                            background_color: 0.18, 0.18, 0.26, 1
                            on_release: root.close_game()
                # Right column: image top-right, description bottom-right
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: 0.5
                    spacing: 16
                    Image:
                        source: app.hangman_image
                        size_hint_y: 0.5
                        allow_stretch: True
                        keep_ratio: True
                    Label:
                        text: 'This game mode was going to be offered but was not finished on time. The idea of the game was to draw a robot arm as the user guessed incorrectly. We had three words chosen for the user to guess. The YOLOv5 model was going to read the image, invert the image, and process the users move by advancing the robot arm or drawing the letter in the corresponding underline. Unfortunately, this game mode was not finished in time.'
                        font_size: 38
                        size_hint_y: 0.5
                        text_size: (self.width - 20, self.height - 20)
                        halign: 'center'
                        valign: 'top'
                        color: 0.82, 0.82, 0.94, 1

<FirstTurnScreen>:
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
            size_hint: 0.78, 0.88
            spacing: 24
            padding: 16
            Label:
                text: 'Who Goes First?'
                font_size: 66
                size_hint_y: None
                height: 96
                bold: True
            Label:
                text: 'Tic Tac Toe - ' + root.selected_difficulty.capitalize()
                font_size: 34
                size_hint_y: None
                height: 58
                color: 0.78, 0.78, 0.86, 1
            StyledButton:
                text: 'Player First\\nYou make the opening move'
                size_hint_y: None
                height: 180
                font_size: 42
                halign: 'center'
                valign: 'middle'
                text_size: self.width - dp(34), self.height - dp(34)
                background_color: 0.2, 0.56, 0.75, 1
                on_release: root.start_ttt('player')
            StyledButton:
                text: 'Robot First\\nThe robot arm makes the opening move'
                size_hint_y: None
                height: 180
                font_size: 42
                halign: 'center'
                valign: 'middle'
                text_size: self.width - dp(34), self.height - dp(34)
                background_color: 0.75, 0.28, 0.28, 1
                on_release: root.start_ttt('rga')
            StyledButton:
                text: '← Back to difficulty'
                font_size: 30
                size_hint_y: None
                height: 88
                background_color: 0.18, 0.18, 0.24, 1
                on_release: root.back_to_ttt_menu()
<GameOverScreen>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 60
        spacing: 30
        Label:
            text: root.title_text     # <--- CHANGED
            font_size: 140
            bold: True
            color: 0.95, 0.25, 0.25, 1
            size_hint_y: 0.35
        Label:
            text: root.message_text   # <--- CHANGED
            font_size: 55
            color: 0.85, 0.85, 0.95, 1
            halign: 'center'
            valign: 'middle'
            text_size: self.width - dp(60), self.height
            size_hint_y: 0.35
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'center'
            size_hint_y: 0.3
            StyledButton:
                text: 'I Have Erased The Board'
                font_size: 55
                size_hint: 0.6, 0.7
                background_color: 0.2, 0.65, 0.35, 1
                on_release: root.board_erased()
""")

def _rga_logo_candidates(base_dir):
    return [
        os.path.join(base_dir, 'OFFICIALRGALogo.png'),
        os.path.join(base_dir, 'OFFICIALRGALogo.PNG'),
        os.path.join(base_dir, 'OfficialRGAlogo.png'),
        os.path.join(base_dir, 'assets', 'OFFICIALRGALogo.png'),
        os.path.join(base_dir, 'assets', 'OFFICIALRGALogo.PNG'),
    ]



def _first_existing(candidates):
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return ''

class GameOverScreen(Screen):
    title_text = StringProperty('GAME OVER')
    message_text = StringProperty('Please erase the whiteboard completely so the robot has a clean slate for the next game.')
    def on_enter(self):
        subprocess.Popen(['rostopic', 'pub', '-1', '/rga_arm_command', 'std_msgs/String', 'wave'])
        
    def fold_arm_background(self):
        subprocess.Popen(['rostopic', 'pub', '-1', '/rga_arm_command', 'std_msgs/String', 'sleep'])
        
    def board_erased(self):
        self.fold_arm_background()
        self.manager.current = 'title'

class TitleScreen(Screen):
    """Kivy Label keeps a minimum size from its text, so we sync in code when the logo is on disk."""

    def _rga_hero_set_fit(self, *args):
        from kivy.app import App
        rimg = self.ids.get('rga_hero')
        app = App.get_running_app()
        if not rimg or not app or not app.rga_uses_file or not hasattr(rimg, 'fit_mode'):
            return
        try:
            # Fill the tall RGA column (most of the black area); may crop edges slightly
            rimg.fit_mode = 'cover'
        except Exception:
            pass

    def on_pre_enter(self, *a):
        from kivy.app import App
        app = App.get_running_app()
        if not app:
            return
        rimg = self.ids.get('rga_hero')
        if rimg and app.rga_uses_file:
            try:
                rimg.funbind('texture', self._rga_hero_set_fit)
            except Exception:
                pass
            self._rga_hero_set_fit()
            rimg.fbind('texture', self._rga_hero_set_fit)
        elif rimg:
            try:
                rimg.funbind('texture', self._rga_hero_set_fit)
            except Exception:
                pass
        rga = self.ids.get('rga_fallback')
        if rga:
            if app.rga_uses_file:
                rga.text = ''
                rga.size_hint = (0, 0)
                rga.opacity = 0
            else:
                rga.text = 'RGA'
                rga.size_hint = (0.84, 0.92)
                rga.opacity = 1


class MenuScreen(Screen):
    selected_game = StringProperty('')

    def on_kv_post(self, base_widget):
        self._sync_menu_layers()

    def on_enter(self, *a):
        self._sync_menu_layers()

    def on_selected_game(self, *args):
        self._sync_menu_layers()

    def _sync_menu_layers(self):
        if not self.ids:
            return
        pl = self.ids.pick_layer
        ttt = self.ids.ttt_layer
        hm = self.ids.hm_layer
        sg = self.selected_game
        if not sg:
            pl.size_hint = (1, 1)
            pl.pos = (0, 0)
            pl.disabled = False
            pl.opacity = 1
            ttt.size_hint = (0, 0)
            ttt.disabled = True
            ttt.opacity = 0
            hm.size_hint = (0, 0)
            hm.disabled = True
            hm.opacity = 0
        elif sg == 'ttt':
            pl.size_hint = (0, 0)
            pl.disabled = True
            pl.opacity = 0
            ttt.size_hint = (1, 1)
            ttt.pos = (0, 0)
            ttt.disabled = False
            ttt.opacity = 1
            hm.size_hint = (0, 0)
            hm.disabled = True
            hm.opacity = 0
        elif sg == 'hm':
            pl.size_hint = (0, 0)
            pl.disabled = True
            pl.opacity = 0
            ttt.size_hint = (0, 0)
            ttt.disabled = True
            ttt.opacity = 0
            hm.size_hint = (1, 1)
            hm.pos = (0, 0)
            hm.disabled = False
            hm.opacity = 1

    def open_game(self, key):
        self.selected_game = key

    def close_game(self):
        self.selected_game = ''

    def choose_ttt_difficulty(self, difficulty):
        first_turn = self.manager.get_screen('first_turn')
        first_turn.selected_difficulty = difficulty
        self.manager.current = 'first_turn'

    def start_hangman(self):
        # with open('/tmp/vrom_game_request.txt', 'w') as f:
        #     f.write("hangman,normal")
        # App.get_running_app().stop()
        pass


class FirstTurnScreen(Screen):
    selected_difficulty = StringProperty('easy')

    def start_ttt(self, first_turn):
        with open('/tmp/vrom_game_request.txt', 'w') as f:
            f.write(f"tictactoe,{self.selected_difficulty}")
        with open('/tmp/vrom_first_turn.txt', 'w') as f:
            f.write(first_turn)
        App.get_running_app().stop()

    def back_to_ttt_menu(self):
        self.manager.get_screen('menu').selected_game = 'ttt'
        self.manager.current = 'menu'


class MainApp(App):
    rga_logo = StringProperty('')
    rga_uses_file = BooleanProperty(False)
    tictactoe_image = StringProperty('')
    hangman_image = StringProperty('')
    
    def shutdown_system(self):
        os.system("killall -2 roslaunch")
        self.stop()

    def _build_app_paths(self):
        base = os.path.dirname(os.path.abspath(__file__))
        self.rga_logo = _first_existing(_rga_logo_candidates(base))
        self.rga_uses_file = bool(self.rga_logo)
        self.tictactoe_image = _first_existing(
            [
                os.path.join(base, 'assets', 'tictactoe.png'),
                os.path.join(base, 'assets', 'tictactoe.jpg'),
                os.path.join(base, 'assets', 'tictactoe.gif'),
            ]
        )
        self.hangman_image = _first_existing(
            [
                os.path.join(base, 'assets', 'hangman.png'),
                os.path.join(base, 'assets', 'hangman.jpg'),
                os.path.join(base, 'assets', 'hangman.gif'),
            ]
        )

    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        self._build_app_paths()
        root = ScreenManager(transition=SlideTransition(duration=0.25))
        root.add_widget(TitleScreen(name='title'))
        root.add_widget(MenuScreen(name='menu'))
        root.add_widget(FirstTurnScreen(name='first_turn'))
        
        # We need to capture the game_over screen object to modify it
        go_screen = GameOverScreen(name='game_over')
        root.add_widget(go_screen)
        
        game_over_flag = '/tmp/vrom_game_over.txt'
        if os.path.exists(game_over_flag):
            # Read the reason from the file
            with open(game_over_flag, 'r') as f:
                reason = f.read().strip()
            os.remove(game_over_flag)
            
            # Change the GUI text based on the reason
            if reason == 'apology_absent':
                go_screen.title_text = 'GAME ABORTED'
                go_screen.message_text = 'You left the play area for too long. Please erase the board completely to start a new game.'
            elif reason == 'apology_scan':
                go_screen.title_text = 'VISION ERROR'
                go_screen.message_text = 'The robot could not clearly read the board after multiple attempts. Please erase the board and try again!'
            elif reason == 'human_win':
                go_screen.title_text = 'YOU WIN!'
                go_screen.message_text = 'Congratulations on beating the robot! Please erase the whiteboard completely for the next game.'
            elif reason == 'robot_win':
                go_screen.title_text = 'ROBOT WINS!'
                go_screen.message_text = 'Better luck next time! Please erase the whiteboard completely.'
            elif reason == 'draw':
                go_screen.title_text = 'DRAW!'
                go_screen.message_text = 'It is a tie! Please erase the whiteboard completely.'
            else:
                go_screen.title_text = 'GAME OVER'
                go_screen.message_text = 'Please erase the whiteboard completely so the robot has a clean slate for the next game.'
                
            root.current = 'game_over'
        else:
            root.current = 'title'
            
        return root


if __name__ == '__main__':
    MainApp().run()
