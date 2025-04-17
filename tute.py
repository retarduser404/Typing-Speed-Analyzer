import curses
import random
import time
import json
import os
from datetime import datetime
import textwrap

COLOR_DEFAULT = 0
COLOR_CORRECT = 1
COLOR_INCORRECT = 2
COLOR_HIGHLIGHT = 3
COLOR_STATUS = 4

def init_colors():
    curses.init_pair(COLOR_CORRECT, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_INCORRECT, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_STATUS, curses.COLOR_CYAN, curses.COLOR_BLACK)

def centered_text(stdscr, y, text, color_pair=COLOR_DEFAULT):
    h, w = stdscr.getmaxyx()
    x = max(0, (w - len(text)) // 2)
    try:
        stdscr.addstr(y, x, text, curses.color_pair(color_pair))
    except curses.error:
        pass

def draw_button(stdscr, y, text, selected=False):
    h, w = stdscr.getmaxyx()
    x = (w - len(text) - 4) // 2
    button_text = f"[ {text} ]"
    color = COLOR_HIGHLIGHT if selected else COLOR_DEFAULT
    try:
        stdscr.addstr(y, x, button_text, curses.color_pair(color))
    except curses.error:
        pass

def animated_start_screen(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "FingerSprint Typing Analyzer"
    subtitle = "Test your typing speed and accuracy"
    for i in range(1, 6):
        centered_text(stdscr, h//2 - 3, "." * i, COLOR_HIGHLIGHT)
        centered_text(stdscr, h//2 - 2, title)
        centered_text(stdscr, h//2, subtitle)
        stdscr.refresh()
        time.sleep(0.1)
    centered_text(stdscr, h//2 + 3, "Press any key to begin...", COLOR_STATUS)
    stdscr.refresh()
    stdscr.getkey()

def get_user_name(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    centered_text(stdscr, h//2 - 2, "Enter your name:", COLOR_STATUS)
    curses.echo()
    curses.curs_set(1)
    name = ""
    while True:
        centered_text(stdscr, h//2, name + "_", COLOR_HIGHLIGHT)
        key = stdscr.getkey()
        if key == '\n' and name.strip():
            break
        elif key in ('\b', '\x7f', '\x08'):
            name = name[:-1]
        elif len(key) == 1 and len(name) < 20:
            name += key
    curses.noecho()
    curses.curs_set(0)
    return name.strip()

def load_text(difficulty="medium"):
    try:
        with open("paras.txt", "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        if not lines:
            return "Error: paras.txt is empty. Add some paragraphs."
        lines.sort(key=len)
        if difficulty == "easy":
            return random.choice(lines[:len(lines)//3])
        elif difficulty == "hard":
            return random.choice(lines[-len(lines)//3:])
        else:
            return random.choice(lines[len(lines)//3:-len(lines)//3])
    except FileNotFoundError:
        return "Error: paras.txt not found in:\n" + os.getcwd()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def select_difficulty(stdscr):
    difficulties = ["Easy", "Medium", "Hard"]
    selected = 1
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        centered_text(stdscr, h//2 - 3, "Select Difficulty:", COLOR_STATUS)
        for i, diff in enumerate(difficulties):
            draw_button(stdscr, h//2 + i, diff, i == selected)
        key = stdscr.getkey()
        if key == '\x1b':
            return "medium"
        elif key in ('\n', '\r'):
            return difficulties[selected].lower()
        elif key == 'KEY_UP':
            selected = max(0, selected - 1)
        elif key == 'KEY_DOWN':
            selected = min(len(difficulties) - 1, selected + 1)

def display_text(stdscr, target, current, wpm=0, accuracy=0, time_left=60):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    wrapped_lines = textwrap.wrap(target, w - 4)
    for i, line in enumerate(wrapped_lines[:h-4]):
        try:
            stdscr.addstr(i, 2, line)
        except curses.error:
            pass
    current_pos = sum(len(line) for line in wrapped_lines[:len(wrapped_lines)-1]) + len(current)
    current_line = 0
    current_col = 0
    chars_so_far = 0
    for i, line in enumerate(wrapped_lines):
        if current_pos < chars_so_far + len(line):
            current_line = i
            current_col = current_pos - chars_so_far
            break
        chars_so_far += len(line)
    try:
        stdscr.addstr(current_line, current_col + 2, "_", curses.color_pair(COLOR_HIGHLIGHT))
    except curses.error:
        pass
    status_bar = f" WPM: {wpm} | Accuracy: {accuracy:.1f}% | Time: {time_left}s "
    try:
        stdscr.addstr(h-2, (w - len(status_bar))//2, status_bar, curses.color_pair(COLOR_STATUS))
    except curses.error:
        pass
    for i, char in enumerate(current):
        correct_char = target[i] if i < len(target) else ' '
        color = COLOR_CORRECT if char == correct_char else COLOR_INCORRECT
        try:
            line = 0
            col = i
            for wrapped_line in wrapped_lines:
                if col < len(wrapped_line):
                    stdscr.addstr(line, col + 2, char, curses.color_pair(color))
                    break
                col -= len(wrapped_line)
                line += 1
        except curses.error:
            continue

def calculate_stats(target, current, elapsed_time):
    if not current or not target:
        return 0, 0, 0, 0
    min_length = min(len(target), len(current))
    correct_chars = sum(1 for i in range(min_length) if current[i] == target[i])
    accuracy = (correct_chars / len(target)) * 100 if target else 0.0
    gross_wpm = (len(current) / 5) / (elapsed_time / 60)
    net_wpm = gross_wpm * (accuracy / 100)
    return round(net_wpm), round(gross_wpm), round(accuracy, 1), correct_chars

def typing_test(stdscr, name, difficulty="medium"):
    target_text = load_text(difficulty)
    if target_text.startswith("Error"):
        stdscr.clear()
        stdscr.addstr(target_text)
        stdscr.addstr("\n\nPress any key to exit")
        stdscr.refresh()
        stdscr.getkey()
        return 0, 0, 0, 0
    current_text = []
    start_time = time.time()
    stdscr.nodelay(True)
    time_limit = 60
    has_started_typing = False
    while True:
        time_elapsed = time.time() - start_time
        time_left = max(time_limit - int(time_elapsed), 0)
        net_wpm, gross_wpm, accuracy, correct_chars = calculate_stats(target_text, current_text, time_elapsed)
        display_text(stdscr, target_text, current_text, net_wpm, accuracy, time_left)
        if has_started_typing and (time_left <= 0 or len(current_text) >= len(target_text)):
            stdscr.nodelay(False)
            break
        try:
            key = stdscr.getkey()
        except:
            continue
        if key == '\x1b':
            return 0, 0, 0, 0
        if key in ('\b', '\x7f', '\x08'):
            if current_text:
                current_text.pop()
        elif len(key) == 1 and len(current_text) < len(target_text):
            current_text.append(key)
            has_started_typing = True
    return net_wpm, gross_wpm, accuracy, correct_chars

def save_score(name, net_wpm, gross_wpm, accuracy, correct_chars, difficulty):
    try:
        scores = load_scores()
        scores.append({
            'name': name,
            'net_wpm': net_wpm,
            'gross_wpm': gross_wpm,
            'accuracy': accuracy,
            'correct_chars': correct_chars,
            'difficulty': difficulty,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        scores.sort(key=lambda x: (x['net_wpm'], x['accuracy']), reverse=True)
        with open('scores.json', 'w') as f:
            json.dump(scores[:10], f, indent=2)
    except Exception as e:
        print(f"Error saving scores: {e}")

def load_scores():
    try:
        with open('scores.json', 'r') as f:
            scores = json.load(f)
            for score in scores:
                if 'difficulty' not in score:
                    score['difficulty'] = "medium"
                if 'net_wpm' not in score:
                    score['net_wpm'] = score.get('wpm', 0)
                if 'gross_wpm' not in score:
                    score['gross_wpm'] = score.get('wpm', 0)
                if 'correct_chars' not in score:
                    score['correct_chars'] = 0
            return scores
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def display_results(stdscr, net_wpm, gross_wpm, accuracy, correct_chars, difficulty):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    centered_text(stdscr, h//2 - 5, "Test Results", COLOR_HIGHLIGHT)
    centered_text(stdscr, h//2 - 3, f"Net WPM: {net_wpm}", COLOR_CORRECT)
    centered_text(stdscr, h//2 - 2, f"Gross WPM: {gross_wpm}")
    centered_text(stdscr, h//2 - 1, f"Accuracy: {accuracy}%")
    centered_text(stdscr, h//2 + 0, f"Correct Characters: {correct_chars}")
    centered_text(stdscr, h//2 + 1, f"Difficulty: {difficulty.capitalize()}")
    centered_text(stdscr, h//2 + 4, "Press any key to continue...", COLOR_STATUS)
    stdscr.refresh()
    stdscr.getkey()

def display_leaderboard(stdscr):
    scores = load_scores()
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    centered_text(stdscr, 1, "Leaderboard", COLOR_HIGHLIGHT)
    if not scores:
        centered_text(stdscr, h//2, "No scores yet!", COLOR_STATUS)
    else:
        for i, score in enumerate(scores[:10]):
            y_pos = 3 + i
            if y_pos >= h - 2:
                break
            timestamp = score.get('timestamp', 'Unknown date')
            line = (f"{i+1}. {score['name']:15} {score['net_wpm']:3} WPM "
                   f"({score['accuracy']:.1f}%) {score['difficulty'].capitalize():6}")
            try:
                stdscr.addstr(y_pos, 2, line)
            except curses.error:
                pass
    centered_text(stdscr, h - 2, "Press any key to continue...", COLOR_STATUS)
    stdscr.refresh()
    stdscr.getkey()

def main_menu(stdscr):
    curses.curs_set(0)
    init_colors()
    options = ["Start Test", "Leaderboard", "Exit"]
    selected = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        centered_text(stdscr, h//2 - 5, "FingerSprint Typing Analyzer", COLOR_HIGHLIGHT)
        for i, option in enumerate(options):
            draw_button(stdscr, h//2 - 2 + i*2, option, i == selected)
        centered_text(stdscr, h - 2, "Use ↑↓ arrows to select, Enter to confirm", COLOR_STATUS)
        stdscr.refresh()
        key = stdscr.getkey()
        if key == '\x1b':
            break
        elif key in ('\n', '\r'):
            if selected == 0:
                name = get_user_name(stdscr)
                difficulty = select_difficulty(stdscr)
                net_wpm, gross_wpm, accuracy, correct_chars = typing_test(stdscr, name, difficulty)
                if net_wpm > 0:
                    save_score(name, net_wpm, gross_wpm, accuracy, correct_chars, difficulty)
                    display_results(stdscr, net_wpm, gross_wpm, accuracy, correct_chars, difficulty)
            elif selected == 1:
                display_leaderboard(stdscr)
            elif selected == 2:
                break
        elif key == 'KEY_UP':
            selected = max(0, selected - 1)
        elif key == 'KEY_DOWN':
            selected = min(len(options) - 1, selected + 1)

def main(stdscr):
    animated_start_screen(stdscr)
    main_menu(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
