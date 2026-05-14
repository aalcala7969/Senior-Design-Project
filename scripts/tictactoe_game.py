#!/usr/bin/env python3
import sys
import os
import time
import threading
import rospy
from std_msgs.msg import String, Int32

# Safety: max scans per human turn before aborting with apology.
# Triggered when the camera feed is glitching and we can't read the move.
MAX_SCANS_PER_TURN = 6

# Presence safety thresholds (seconds).
PRESENCE_GRACE   = 5.0   # quiet wait — user can briefly leave the play zone
PRESENCE_TIMEOUT = 10.0  # countdown after grace; if still absent → abort

# Exit codes consumed by master.py to drive the GameOver screen text.
EXIT_NORMAL       = 0
EXIT_HUMAN_WIN    = 1
EXIT_ROBOT_WIN    = 2
EXIT_DRAW         = 3
EXIT_ABSENT       = 10
EXIT_SCAN_FAILURE = 11

WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)

class GameAborted(Exception):
    """Raised inside blocking helpers to unwind cleanly when the safety
    monitor decides the game must end."""


class TicTacToeGame:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.board = [" "] * 9
        self.ai_player    = "X"
        self.human_player = "O"

        rospy.init_node('rga_tictactoe', anonymous=True)
        rospy.Subscriber('/vision_detections', String, self.vision_callback)
        rospy.Subscriber('/rga_arm_status',    String, self.status_callback)
        rospy.Subscriber('/game_state',        Int32,  self.game_state_callback)

        self.arm_pub = rospy.Publisher('/rga_arm_command',  String, queue_size=10)

        self._arm_done       = threading.Event()
        self.latest_vision_data = []

        # Safety state — read by the monitor thread, written by the
        # game_state callback.
        self.game_state = 0
        self.exit_reason = None

        # Spin up the presence monitor immediately. It's a daemon so it
        # dies with the process if anything else goes wrong.
        self._monitor_thread = threading.Thread(
            target=self._presence_monitor, daemon=True)
        self._monitor_thread.start()

    # ─────────────────────────────────────────────────────────────────────────
    # ROS callbacks
    # ─────────────────────────────────────────────────────────────────────────
    def status_callback(self, msg):
        if msg.data == "done":
            self._arm_done.set()

    def vision_callback(self, msg):
        if not msg.data:
            return
        for item in msg.data.split(','):
            parts = item.split(':')
            if len(parts) == 2:
                entry = (parts[0], int(parts[1]))
                if entry not in self.latest_vision_data:
                    self.latest_vision_data.append(entry)

    def game_state_callback(self, msg):
        self.game_state = msg.data

    # ─────────────────────────────────────────────────────────────────────────
    # Safety monitor — runs in its own thread for the entire game.
    # Triggers EXIT_ABSENT when the user leaves the play zone and doesn't
    # come back within PRESENCE_GRACE + PRESENCE_TIMEOUT seconds.
    # ─────────────────────────────────────────────────────────────────────────
    def _presence_monitor(self):
        while not rospy.is_shutdown() and self.exit_reason is None:
            if self.game_state == 3:
                time.sleep(0.2)
                continue

            # User just stepped out. Quiet 5s grace window — they may have
            # only leaned away to grab the marker.
            grace_start = time.time()
            while time.time() - grace_start < PRESENCE_GRACE:
                if self.exit_reason is not None:
                    return
                if self.game_state == 3:
                    break
                time.sleep(0.1)
            else:
                # Grace expired; escalate with a visible countdown.
                print("\n[RGA SAFETY] Player left the play zone.")
                print(f"[RGA SAFETY] Resuming if you return within {int(PRESENCE_TIMEOUT)} s...")
                countdown_start = time.time()
                last_announced = None
                returned = False
                while time.time() - countdown_start < PRESENCE_TIMEOUT:
                    if self.exit_reason is not None:
                        return
                    if self.game_state == 3:
                        returned = True
                        break
                    remaining = int(PRESENCE_TIMEOUT - (time.time() - countdown_start)) + 1
                    if remaining != last_announced:
                        print(f"  ... {remaining}")
                        last_announced = remaining
                    time.sleep(0.1)

                if returned:
                    print("[RGA SAFETY] Player returned. Resuming game.\n")
                else:
                    print("\n[RGA SAFETY] No player detected. Ending game.")
                    self.exit_reason = 'absent'
                    self._arm_done.set()  # unblock any wait_for_arm
                    return

    def _check_abort(self):
        if self.exit_reason is not None:
            raise GameAborted(self.exit_reason)

    def _interruptible_sleep(self, duration):
        """time.sleep that bails out if the safety monitor aborts."""
        end = time.time() + duration
        while time.time() < end:
            self._check_abort()
            time.sleep(min(0.1, end - time.time()))

    # ─────────────────────────────────────────────────────────────────────────
    # Arm helpers
    # ─────────────────────────────────────────────────────────────────────────
    def wait_for_arm(self, timeout=120):
        # Poll in short chunks so an abort raised by the monitor thread
        # can unwind us instead of hanging here for two minutes.
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self._arm_done.wait(0.2):
                self._arm_done.clear()
                self._check_abort()
                return
            self._check_abort()
        self._arm_done.clear()

    def send_arm(self, cmd):
        self._arm_done.clear()
        self.arm_pub.publish(cmd)
        self.wait_for_arm()

    # ─────────────────────────────────────────────────────────────────────────
    # Game logic
    # ─────────────────────────────────────────────────────────────────────────
    def check_winner(self, board):
        for a, b, c in WIN_LINES:
            if board[a] != " " and board[a] == board[b] == board[c]:
                return board[a]
        return None

    def is_draw(self, board):
        return all(cell != " " for cell in board) and self.check_winner(board) is None

    def valid_moves(self, board):
        return [i for i, v in enumerate(board) if v == " "]

    def minimax(self, board, player, ai, human):
        winner = self.check_winner(board)
        if winner == ai:    return  1, None
        if winner == human: return -1, None
        if self.is_draw(board): return 0, None

        moves = self.valid_moves(board)
        if player == ai:
            best, best_m = -2, None
            for m in moves:
                board[m] = player
                score, _ = self.minimax(board, human, ai, human)
                board[m] = " "
                if score > best: best, best_m = score, m
            return best, best_m
        else:
            best, best_m = 2, None
            for m in moves:
                board[m] = player
                score, _ = self.minimax(board, ai, ai, human)
                board[m] = " "
                if score < best: best, best_m = score, m
            return best, best_m

    # ─────────────────────────────────────────────────────────────────────────
    # Drawing
    # ─────────────────────────────────────────────────────────────────────────
    def draw_game_board(self):
        print("\n[RGA SYSTEM] Drawing tic-tac-toe grid...")
        self.send_arm("draw,tictactoemap.txt")
        self.send_arm("reset")
        print("[RGA ARM] Board drawing complete.\n")

    def execute_robot_move(self, cell_index):
        print(f"[RGA ARM] Drawing X in cell {cell_index}")
        self.send_arm(f"draw,draw_X_{cell_index}.txt")
        self.send_arm("reset")

    # ─────────────────────────────────────────────────────────────────────────
    # Vision / scan
    # ─────────────────────────────────────────────────────────────────────────
    def move_to_observation_pose(self):
        print("[RGA GAME] Requesting board scan...")
        self.send_arm("scan")

    def wait_for_human_move(self):
        """Iterative scan loop with a hard per-turn budget. If the camera
        feed is glitching and we burn through MAX_SCANS_PER_TURN attempts
        without a clear read, set scan_failure and let run() abort."""
        print("\n[RGA GAME] Your turn! Draw an 'O' on the board.")
        print("[RGA GAME] Scanning in:")
        for i in range(5, 0, -1):
            print(f"  ... {i}")
            self._interruptible_sleep(1.0)

        for attempt in range(1, MAX_SCANS_PER_TURN + 1):
            self._check_abort()
            self.latest_vision_data = []
            self.move_to_observation_pose()
            self._interruptible_sleep(0.5)

            print(f"[RGA VISION] Processing scan {attempt}/{MAX_SCANS_PER_TURN}...")
            empty_cells = self.valid_moves(self.board)
            detected_moves = [
                cell for piece, cell in self.latest_vision_data
                if piece.upper() == self.human_player.upper() and cell in empty_cells
            ]
            unique_moves = list(set(detected_moves))

            if len(unique_moves) == 1:
                locked = unique_moves[0]
                print(f"[RGA VISION] Move verified: Cell {locked}.")
                return locked

            remaining = MAX_SCANS_PER_TURN - attempt
            if remaining > 0:
                print(f"[RGA ERROR] Move unclear. Retrying ({remaining} left)...")
                self._interruptible_sleep(3.0)

        print(f"\n[RGA ERROR] Failed to read board after {MAX_SCANS_PER_TURN} scans.")
        self.exit_reason = 'scan_failure'
        raise GameAborted('scan_failure')

    # ─────────────────────────────────────────────────────────────────────────
    # Main loop
    # ─────────────────────────────────────────────────────────────────────────
    def run(self):
        print(f"\n[RGA SYSTEM] Starting Tic-Tac-Toe — difficulty: {self.difficulty.upper()}")
        print("[RGA SYSTEM] Robot = X  |  Human = O")

        human_turn   = False
        first_file   = '/tmp/vrom_first_turn.txt'
        if os.path.exists(first_file):
            with open(first_file) as f:
                if f.read().strip() == 'player':
                    human_turn = True
            os.remove(first_file)

        print(f"[RGA SYSTEM] {'Human' if human_turn else 'Robot'} goes first.")

        try:
            self._interruptible_sleep(1.0)
            self.draw_game_board()

            final_code = EXIT_NORMAL # <--- ADD THIS
            
            while not rospy.is_shutdown():
                self._check_abort()

                if human_turn:
                    print("\n--- HUMAN TURN ---")
                    move = self.wait_for_human_move()
                    self.board[move] = self.human_player
                else:
                    print("\n--- ROBOT TURN ---")
                    if self.difficulty == 'hard':
                        _, move = self.minimax(
                            self.board, self.ai_player, self.ai_player, self.human_player)
                    else:
                        move = self.valid_moves(self.board)[0]

                    print(f"[RGA AI] Optimal move: Cell {move}")
                    self.execute_robot_move(move)
                    self.board[move] = self.ai_player

                winner = self.check_winner(self.board)
                if winner:
                    label = 'Human' if winner == self.human_player else 'Robot'
                    print(f"\n[RGA SYSTEM] GAME OVER — {label} Wins!")
                    # ---> ASSIGN CODE HERE <---
                    final_code = EXIT_HUMAN_WIN if winner == self.human_player else EXIT_ROBOT_WIN
                    break

                if self.is_draw(self.board):
                    print("\n[RGA SYSTEM] GAME OVER — Draw!")
                    # ---> ASSIGN CODE HERE <---
                    final_code = EXIT_DRAW
                    break

                human_turn = not human_turn

            return final_code # <--- CHANGE THIS FROM EXIT_NORMAL
        
        except GameAborted as e:
            # Don't try to wave/sleep when the player isn't there — the
            # arm just stays put and master.py / GameOverScreen handle UX.
            print(f"[RGA SYSTEM] Game aborted: {e}")
            if e.args and e.args[0] == 'scan_failure':
                return EXIT_SCAN_FAILURE
            return EXIT_ABSENT


if __name__ == "__main__":
    difficulty = sys.argv[1] if len(sys.argv) > 1 else 'hard'
    code = EXIT_NORMAL
    try:
        game = TicTacToeGame(difficulty)
        code = game.run()
    except rospy.ROSInterruptException:
        pass
    except KeyboardInterrupt:
        print("\n[RGA SYSTEM] Game Terminated Safely.")
    sys.exit(code)
