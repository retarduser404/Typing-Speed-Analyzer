import curses
import random
import time
import json


def start_screen(stdscr):
    stdscr.clear()
    stdscr.addstr("Welcome to FingerSprint! Check your typing skills in a minute.")
    stdscr.addstr("\nPress any key to begin!")
    stdscr.refresh()
    stdscr.getkey()


def display_text(stdscr, target, current, wpm=0, accuracy=0, time_left=60):
    h, w = stdscr.getmaxyx()
    stdscr.addstr(0, 0, target[:w - 1])
    status_bar = f"WPM: {wpm} | Accuracy: {accuracy:.2f}% | Time left: {time_left}s"
    stdscr.addstr(1, 0, status_bar[:w - 1], curses.color_pair(1))

    for i, char in enumerate(current):
        correct_char = target[i]
        color = curses.color_pair(1) if char == correct_char else curses.color_pair(2)
        try:
            stdscr.addstr(0, i, char, color)
        except curses.error:
            continue


def load_text():
    try:
        with open("paras.txt", "r") as f:
            lines = f.readlines()
            return random.choice(lines).strip()
    except FileNotFoundError:
        return "No text file found. Please provide a valid 'paras.txt' file."


def calculate_accuracy(target, current):
    if len(target) == 0:
        return 0.0
    correct_chars = sum(1 for i, char in enumerate(current) if char == target[i])
    return round((correct_chars / len(target)) * 100, 2)


def wpm_test(stdscr):
    target_text = load_text()
    current_text = []
    start_time = time.time()
    stdscr.nodelay(True)
    time_limit = 60  # 1 minute time limit

    while True:
        time_elapsed = max(time.time() - start_time, 1e-5)  # Ensure time_elapsed is never zero
        time_left = max(time_limit - int(time_elapsed), 0)
        wpm = round((len(current_text) / (time_elapsed / 60)) / 5)
        accuracy = calculate_accuracy(target_text, current_text)

        stdscr.clear()
        display_text(stdscr, target_text, current_text, wpm, accuracy, time_left)
        stdscr.refresh()

        if time_left <= 0 or "".join(current_text) == target_text or len(current_text) >= len(target_text):
            stdscr.nodelay(False)
            break

        try:
            key = stdscr.getkey()
        except curses.error:
            continue

        if key == '\x1b':  # ESC key
            break

        if key in ('\b', '\x7f'):  # Backspace keys
            if len(current_text) > 0:
                current_text.pop()
        elif len(current_text) < len(target_text):
            current_text.append(key)

    return wpm, accuracy


def save_score(stdscr, wpm, accuracy):
    scores = load_scores()
    curses.endwin()
    stdscr.clear()
    stdscr.addstr("Enter your name: ")
    stdscr.refresh()
    curses.echo()
    name = stdscr.getstr().decode('utf-8')  # Read input directly from stdscr
    curses.noecho()
    scores.append({'name': name, 'wpm': wpm, 'accuracy': accuracy})
    scores = sorted(scores, key=lambda x: x['wpm'], reverse=True)[:10]  # Keep top 10 scores

    try:
        with open('scores.json', 'w') as f:
            json.dump(scores, f)
    except IOError:
        stdscr.addstr("Error saving scores to file.")
        stdscr.refresh()
        stdscr.getch()  # Wait for key press before continuing


def load_scores():
    try:
        with open('scores.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def display_leaderboard(stdscr):
    scores = load_scores()
    stdscr.clear()
    stdscr.addstr("Leaderboard\n", curses.color_pair(1))

    for i, score in enumerate(scores):
        stdscr.addstr(f"{i + 1}. {score['name']} - WPM: {score['wpm']} Accuracy: {score['accuracy']}%\n",
                      curses.color_pair(1))

    stdscr.addstr("\nPress any key to continue")
    stdscr.refresh()
    stdscr.getkey()


def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    start_screen(stdscr)
    while True:
        wpm, accuracy = wpm_test(stdscr)
        save_score(stdscr, wpm, accuracy)  # Pass stdscr to save_score
        stdscr.clear()
        display_leaderboard(stdscr)
        stdscr.addstr(2, 0, "You completed the test! Press any key to continue or ESC to exit")
        key = stdscr.getkey()

        if key == '\x1b':
            break


if __name__ == "__main__":
    curses.wrapper(main)
