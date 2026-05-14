#!/usr/bin/env python3

import rospy
import subprocess
import os
import time
from std_msgs.msg import Int32

class MasterFSM:
    def __init__(self):
        rospy.init_node('rga_master', anonymous=True)
        
        # ESP32 game_state values:
        #   0 = ADC off (system idle)
        #   1 = ADC on, no one detected
        #   2 = warning zone — wake screen, allow GUI navigation only
        #   3 = play zone — robot motion gated on this
        self.user_state = 0
        rospy.Subscriber('/game_state', Int32, self.state_callback)
        
        self.kivy_process = None
        self.vision_process = None
        self.game_config_file = '/tmp/vrom_game_request.txt'
        self.script_dir = os.path.expanduser('~/catkin_ws/src/senior_design/scripts')
        
        print("Booting Arm Controller")
        arm_script = os.path.join(self.script_dir, 'arm_controller.py')
        self.arm_process = subprocess.Popen(['python3', arm_script, "tictactoe"], cwd=self.script_dir)
        
        rospy.loginfo("Master FSM Initialized. Waiting for ESP32...")

    def state_callback(self, msg):
        self.user_state = msg.data

    def launch_gui(self):
        #"""Starts Kivy if it isn't running."""
        if self.kivy_process is None or self.kivy_process.poll() is not None:
            rospy.loginfo("Launching Kivy GUI...")
            app_path = os.path.join(self.script_dir, 'app.py')
            self.kivy_process = subprocess.Popen(['python3', app_path], cwd=self.script_dir)

    def kill_gui(self):
        #"""Kills Kivy to free up GPU/RAM for PyTorch."""
        if self.kivy_process and self.kivy_process.poll() is None:
            rospy.loginfo("Terminating Kivy GUI to free RAM...")
            self.kivy_process.terminate()
            self.kivy_process.wait()
            self.kivy_process = None

    def display_control(self, state):
        #"""Manages OS-level screen dimming based on ESP32 state."""
        if state < 2:
            # Dim or turn off screen (Linux xset command)
            os.system("xset dpms force standby")
        else:
            # Wake up screen
            os.system("xset dpms force on")

    def wait_for_play_state(self):
        """Blocks until game_state == 3 (user in play zone) before starting robot movement."""
        rospy.loginfo("Waiting for user to enter play zone (game_state == 3)...")
        rate = rospy.Rate(5)
        while not rospy.is_shutdown():
            if self.user_state == 3:
                rospy.loginfo("Play zone confirmed. Starting game.")
                return True
            if self.user_state < 2:
                rospy.logwarn("User left the area. Aborting game launch.")
                return False
            rate.sleep()
        return False

    def run(self):
        rate = rospy.Rate(10) # 10 Hz

        while not rospy.is_shutdown():
            self.display_control(self.user_state)

            # State 2+: User is in warning zone — show the GUI so they can choose a game
            if self.user_state >= 2 and not os.path.exists(self.game_config_file):
                self.launch_gui()

            # A game has been selected via the GUI
            elif os.path.exists(self.game_config_file):
                rospy.loginfo("Game Request Detected! Transitioning to Headless Mode.")

                # 1. Kill the GUI
                self.kill_gui()
                time.sleep(1.5)

                # 2. Read the requested game and difficulty
                with open(self.game_config_file, 'r') as f:
                    game_mode = f.read().strip()
                os.remove(self.game_config_file)

                game_type, difficulty = game_mode.split(',')
                rospy.loginfo(f"Game selected: {game_mode}")

                # 3. Gate: robot must NOT move until user is in play zone (state == 3)
                if not self.wait_for_play_state():
                    rospy.logwarn("Play zone not reached. Returning to menu.")
                    self.launch_gui()
                    rate.sleep()
                    continue

                # tictactoe_game.py exit codes drive the GameOver text:
                #   0  → normal end
                #   10 → user left the play zone (apology_absent)
                #   11 → camera/scan failure (apology_scan)
                exit_code = 0
                if game_type == "tictactoe":
                    rospy.loginfo("Launching YOLOv5 for TicTacToe Vision...")
                    self.vision_process = subprocess.Popen(['python3', '/home/jetson/yolov5/vision.py'])

                    game_script = os.path.join(self.script_dir, 'tictactoe_game.py')
                    result = subprocess.run(['python3', game_script, difficulty], cwd=self.script_dir)
                    exit_code = result.returncode

                elif game_type == "hangman":
                    rospy.logwarn("Hangman mode is disabled. Ignoring request.")
                    exit_code = 0 # Failsafe exit code
#                     rospy.loginfo("Launching YOLOv5 for Hangman Vision...")
#                     hangman_vision_script = os.path.join(self.script_dir, 'hangman_vision.py')
#                     self.vision_process = subprocess.Popen(['python3', hangman_vision_script], cwd=self.script_dir)

#                     game_script = os.path.join(self.script_dir, 'hangman_game.py')
#                     subprocess.run(['python3', game_script], cwd=self.script_dir)

                # 4. Game Over: clean up and prep for next round
                if self.vision_process:
                    self.vision_process.terminate()

                if exit_code == 10:
                    reason = 'apology_absent'
                elif exit_code == 11:
                    reason = 'apology_scan'
                elif exit_code == 1:
                    reason = 'human_win'
                elif exit_code == 2:
                    reason = 'robot_win'
                elif exit_code == 3:
                    reason = 'draw'
                else:
                    reason = 'normal'

                rospy.loginfo(f"Game Over ({reason}). Awaiting user to erase board...")

                with open('/tmp/vrom_game_over.txt', 'w') as f:
                    f.write(reason)

                self.launch_gui()

            rate.sleep()

if __name__ == '__main__':
    try:
        fsm = MasterFSM()
        fsm.run()
    except rospy.ROSInterruptException:
        pass
