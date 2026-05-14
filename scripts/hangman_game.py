#!/usr/bin/env python3
import sys
import os
import time
import random
import threading
import rospy
from std_msgs.msg import String

class HangmanGame:
    def __init__(self):
        rospy.init_node('rga_hangman', anonymous=True)
        rospy.Subscriber('/vision_detections', String, self.vision_callback)
        rospy.Subscriber('/rga_arm_status', String, self.status_callback)
        
        self.arm_pub = rospy.Publisher('/rga_arm_command', String, queue_size=10)
        self.ik_pub  = rospy.Publisher('/rga_ik_command',  String, queue_size=10)

        self._arm_done = threading.Event()
        self.latest_vision_data = []

        # Game State
        self.word_dict = {1: 'CAPSTONE', 2: 'PAOLINI', 3: 'DOFBOT'}
        self.map_id = random.choice([1, 2, 3])
        self.target_word = self.word_dict[self.map_id]

        self.guessed_letters = set()
        self.strikes = 0
        self.max_strikes = 5
        self.strike_commands = [
            'HANGMAN_HEAD',
            'HANGMAN_TORSO',
            'HANGMAN_ARMS',
            'HANGMAN_LEG1',
            'HANGMAN_LEG2',
        ]

        # ── Board layout (meters) ──────────────────────────────────────────────
        # Whiteboard: ±0.305 m in X, 0.051–0.356 m in Y
        # Gallows occupies left third; word underlines fill right portion.
        self.word_start_x    = -0.060   # Left edge of first underline
        self.letter_spacing  =  0.045   # Center-to-center spacing between letters
        self.underline_width =  0.040   # Width of each underline (4 cm)
        # CAPSTONE (8 letters) last underline ends at -0.060+7*0.045+0.040 = 0.295 m ✓
        self.noose_x =  0.10            # Gallows noose tip X
        self.noose_y =  0.24            # Gallows noose tip Y

    # ─────────────────────────────────────────────────────────────────────────
    # ROS Callbacks
    # ─────────────────────────────────────────────────────────────────────────
    def status_callback(self, msg):
        if msg.data == "done":
            self._arm_done.set()

    def vision_callback(self, msg):
        if not msg.data:
            return
        # vision_hangman publishes format "A:99,B:99"
        for item in msg.data.split(','):
            parts = item.split(':')
            if len(parts) == 2:
                letter = parts[0].upper()
                if letter not in self.latest_vision_data:
                    self.latest_vision_data.append(letter)

    # ─────────────────────────────────────────────────────────────────────────
    # Arm Helpers (TicTacToe Architecture)
    # ─────────────────────────────────────────────────────────────────────────
    def wait_for_arm(self, timeout=120):
        self._arm_done.wait(timeout=timeout)
        self._arm_done.clear()

    def send_arm(self, cmd):
        self._arm_done.clear()
        self.arm_pub.publish(cmd)
        self.wait_for_arm()

    def send_ik(self, cmd):
        self._arm_done.clear()
        self.ik_pub.publish(cmd)
        self.wait_for_arm()

    # ─────────────────────────────────────────────────────────────────────────
    # Drawing Engine
    # ─────────────────────────────────────────────────────────────────────────
    def draw_gallows(self):
        print(f"\n[RGA SYSTEM] Drawing gallows and underlines for a {len(self.target_word)}-letter word...")

        # Gallows: left third of the board
        # Base 20 cm wide, pole 23 cm tall, beam 10 cm, noose 6 cm drop
        gallows_lines = [
            #      x1    y1   x2   y2   z
            "LINE, 0.0, 0.2, 0.15, 0.2, 1",   # Base
            "LINE, 0.7, 0.2, 0.70, 0.8, 1",   # Vertical pole
            "LINE, 0.7, 0.2, 0.10, 0.2, 1",    # Top beam
            f"LINE,{self.noose_x:.4f},0.20,{self.noose_x:.4f},{self.noose_y:.4f},1",  # Noose
            #         x1               y1      x2                y2              z
        ]
        for cmd in gallows_lines:
            self.send_ik(cmd)

        # Word underlines: right portion of the board (y=0.07, same level as base)
        y_line = 0.15
        for i in range(len(self.target_word)):
            xl = self.word_start_x + (i * self.letter_spacing)
            xr = xl + self.underline_width
            self.send_ik(f"LINE,{xl:.4f},{y_line},{xr:.4f},{y_line},1")

        self.send_arm("reset")
        print("[RGA ARM] Board setup complete.\n")

    def draw_letter_at_index(self, letter, index):
        # Center letter over its underline.
        # ik_solver uses ox = cx - LW, so cx = underline_center + LW (LW=0.022 in ik_solver.cpp).
        x_center = self.word_start_x + (index * self.letter_spacing) + 0.042
        y_letter  = 0.085  # Bottom of letter sits 1.5 cm above underline at y=0.07

        cmd = f"LETTER,{letter},{x_center:.4f},{y_letter:.4f}"
        print(f"[RGA ARM] Drawing '{letter}' at index {index}...")
        self.send_ik(cmd)
        self.send_arm("reset")

    def draw_hangman_part(self, part_index):
        cmd = self.strike_commands[part_index]
        print(f"[RGA ARM] Drawing {cmd}...")
        self.send_ik(f"SHAPE,{cmd},{self.noose_x:.4f},{self.noose_y:.4f}")
        self.send_arm("reset")

    # ─────────────────────────────────────────────────────────────────────────
    # Vision & Scanning
    # ─────────────────────────────────────────────────────────────────────────
    def wait_for_guess(self):
        print("\n[RGA GAME] Your turn! Write a letter in the scanning zone.")
        print("[RGA GAME] Scanning in:")
        for i in range(3, 0, -1):
            print(f"  ... {i}")
            time.sleep(1)

        self.latest_vision_data = []
        self.send_arm("scan_hangman")

        print("[RGA VISION] Processing detected letters...")
        new_letters = [l for l in self.latest_vision_data if l not in self.guessed_letters]

        if not new_letters:
            print("[RGA ERROR] No new letters detected. Ensure your writing is clear.")
            print("[RGA GAME] Retrying in 3 seconds...")
            time.sleep(3)
            return self.wait_for_guess()

        # If YOLO detects multiple new letters, take the first one
        locked_guess = new_letters[0]
        print(f"[RGA VISION] Locked in: '{locked_guess}'")
        return locked_guess

    # ─────────────────────────────────────────────────────────────────────────
    # Main Loop
    # ─────────────────────────────────────────────────────────────────────────
    def run(self):
        print("\n=================================")
        print("[RGA SYSTEM] Starting HANGMAN")
        print(f"[RGA SYSTEM] Word length: {len(self.target_word)} letters")
        print("=================================\n")

        # Wait for publisher connections to the IK solver to be established.
        # Publishing before the ROS subscriber handshake is complete drops messages.
        rospy.sleep(1.5)

        self.draw_gallows()

        while not rospy.is_shutdown():
            guess = self.wait_for_guess()
            self.guessed_letters.add(guess)

            if guess in self.target_word:
                print(f"\n[RGA AI] Correct! '{guess}' is in the word.")
                for i, ch in enumerate(self.target_word):
                    if ch == guess:
                        self.draw_letter_at_index(guess, i)

                # Check Win Condition
                if all(ch in self.guessed_letters for ch in self.target_word):
                    print(f"\n[RGA SYSTEM] YOU WIN! The word was {self.target_word}.")
                    self.send_arm("wave")
                    time.sleep(4)
                    break
            else:
                self.strikes += 1
                print(f"\n[RGA AI] Incorrect! Strike {self.strikes}/{self.max_strikes}")
                self.draw_hangman_part(self.strikes - 1)

                # Check Loss Condition
                if self.strikes >= self.max_strikes:
                    print(f"\n[RGA SYSTEM] GAME OVER. The word was {self.target_word}.")
                    break

        self.send_arm("sleep")
        
        # Tell the Master FSM the game is over
        with open('/tmp/vrom_game_over.txt', 'w') as f:
            f.write("game_over")


if __name__ == "__main__":
    try:
        game = HangmanGame()
        game.run()
    except rospy.ROSInterruptException:
        pass
    except KeyboardInterrupt:
        print("\n[RGA SYSTEM] Game Terminated Safely.")