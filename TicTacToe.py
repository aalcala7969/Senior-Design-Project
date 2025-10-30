import os
import sys


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


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def render(board):
    # board is list of 9 items: 'X', 'O', or ' '
    cells = [c if c != " " else str(i + 1) for i, c in enumerate(board)]
    lines = (
        f" {cells[0]} | {cells[1]} | {cells[2]} ",
        "---+---+---",
        f" {cells[3]} | {cells[4]} | {cells[5]} ",
        "---+---+---",
        f" {cells[6]} | {cells[7]} | {cells[8]} ",
    )
    print("\n".join(lines))


def check_winner(board):
    for a, b, c in WIN_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_draw(board):
    return all(cell != " " for cell in board) and check_winner(board) is None


def valid_moves(board):
    return [i for i, v in enumerate(board) if v == " "]


def minimax(board, player, ai_player, human_player):
    # returns (score, move_index)
    winner = check_winner(board)
    if winner == ai_player:
        return 1, None
    if winner == human_player:
        return -1, None
    if is_draw(board):
        return 0, None

    moves = valid_moves(board)
    if player == ai_player:
        best_score = -2
        best_move = None
        for m in moves:
            board[m] = player
            score, _ = minimax(board, human_player, ai_player, human_player)
            board[m] = " "
            if score > best_score:
                best_score = score
                best_move = m
                if best_score == 1:
                    break
        return best_score, best_move
    else:
        best_score = 2
        best_move = None
        for m in moves:
            board[m] = player
            score, _ = minimax(board, ai_player, ai_player, human_player)
            board[m] = " "
            if score < best_score:
                best_score = score
                best_move = m
                if best_score == -1:
                    break
        return best_score, best_move


def get_human_move(board, prompt="Choose a cell (1-9): "):
    moves = valid_moves(board)
    move_set = {str(i + 1) for i in moves}
    while True:
        choice = input(prompt).strip()
        if choice in move_set:
            return int(choice) - 1
        print("Invalid move. Pick an available number (1-9).")


def choose_mode():
    print("Tic Tac Toe")
    print("1) Two player (local)")
    print("2) Play vs Computer (unbeatable)")
    while True:
        choice = input("Select mode (1 or 2): ").strip()
        if choice in ("1", "2"):
            return int(choice)
        print("Enter 1 or 2.")


def choose_symbol():
    while True:
        s = input("Choose your symbol (X goes first) - X or O: ").strip().upper()
        if s in ("X", "O"):
            return s
        print("Enter X or O.")


def play_game():
    while True:
        clear()
        mode = choose_mode()
        if mode == 1:
            p1 = "X"
            p2 = "O"
            board = [" "] * 9
            current = "X"
            while True:
                clear()
                print("Two player mode")
                render(board)
                mover = "Player 1 (X)" if current == "X" else "Player 2 (O)"
                print(f"{mover}'s turn ({current})")
                move = get_human_move(board)
                board[move] = current
                winner = check_winner(board)
                if winner:
                    clear()
                    render(board)
                    print(f"{winner} wins!")
                    break
                if is_draw(board):
                    clear()
                    render(board)
                    print("Draw!")
                    break
                current = "O" if current == "X" else "X"
        else:
            human = choose_symbol()
            ai = "O" if human == "X" else "X"
            human_turn = human == "X"
            board = [" "] * 9
            while True:
                clear()
                print(f"Play vs Computer - You: {human}  Computer: {ai}")
                render(board)
                if human_turn:
                    print("Your move")
                    move = get_human_move(board)
                else:
                    print("Computer is thinking")
                    _, move = minimax(board, ai, ai, human)
                board[move] = human if human_turn else ai
                winner = check_winner(board)
                if winner:
                    clear()
                    render(board)
                    if winner == human:
                        print("You win")
                    else:
                        print("Computer wins")
                    break
                if is_draw(board):
                    clear()
                    render(board)
                    print("Draw!")
                    break
                human_turn = not human_turn

        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("done")
            break


if __name__ == "__main__":
    try:
        play_game()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        sys.exit(0)