import random
import string

WORDS = [
    "python", "gpu","jestonnano", "matrix", "serial", 
    "school", "sdsu", "robot", "thread", "gui",
    "professor", "hand", "arm", "sensor", "display",
]

GALLOWS = [
    "\n\n\n\n\n=====",
    "  |\n  O\n\n\n\n=====",
    "  |\n  O\n  |\n\n\n=====",
    "  |\n  O\n /|\\\n\n\n=====",
    "  |\n  O\n /|\\\n / \\\n\n=====",
    "  |\n \\O\n /|\\\n / \\\n\n=====",
    "  |\n \\O/\n /|\\\n / \\\n\n=====",
]

MAX_MISSES = 6  # you get 6 wrong guesses if you lose you lose :o

def pick_word() -> str:
    return random.choice(WORDS)

def mask_word(secret: str, guesses: set) -> str:
    return " ".join(c if c in guesses else "_" for c in secret)

def draw_board(secret: str, guesses: set, misses: set):
    print(GALLOWS[min(len(misses), MAX_MISSES)])
    print(f"Word:   {mask_word(secret, guesses)}")
    print(f"Misses: {', '.join(sorted(misses)) or '—'}")
    print(f"Guesses:{', '.join(sorted(guesses)) or '—'}")
    print(f"Left:   {MAX_MISSES - len(misses)}\n")

def game_over(secret: str, guesses: set, misses: set) -> bool:
    won = all(c in guesses for c in set(secret))
    lost = len(misses) >= MAX_MISSES and not won
    if won:
        draw_board(secret, guesses, misses)
        print(f"You won! The word was '{secret}'.")
        return True
    if lost:
        draw_board(secret, guesses, misses)
        print(f"You lost. The word was '{secret}'.")
        return True
    return False

def main():
    print("=== Hangman (Terminal) ===")
    print("Type a single letter and press Enter. Type 'quit' to exit.\n")

    secret = pick_word()
    guesses, misses = set(), set()

    while True:
        if game_over(secret, guesses, misses):
            break

        draw_board(secret, guesses, misses)
        raw = input("Your guess: ").strip().lower()

        if raw == "quit":
            print("GoodBye!")
            break

        if len(raw) != 1 or raw not in string.ascii_lowercase:
            print("Please enter a single letter (a-z).\n")
            continue

        if raw in guesses or raw in misses:
            print(f"You already tried '{raw}'.\n")
            continue

        if raw in secret:
            guesses.add(raw)
            print(f"Nice! '{raw}' is in the word.\n")
        else:
            misses.add(raw)
            print(f"Oops! '{raw}' is not in the word.\n")

if __name__ == "__main__":
    main()