import os
import time
import random
import re

# Tree dimensions
HEIGHT = 20
WIDTH = 40
SEPARATOR_WIDTH = 12

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
RESET = '\033[0m'
ORANGE = '\033[38;5;208m'
GOLD = '\033[38;5;220m'
PINK = '\033[38;5;200m'

ALL_COLORS = [RED, YELLOW, BLUE, CYAN, MAGENTA, ORANGE, GOLD, PINK]

LYRICS_TIMINGS = [
    ("Don't cry, snowman, not in front of me", 3.0),
    ("Who'll catch your tears if you can't catch me, darling?", 4.0),
    ("If you can't catch me, darling", 2.5),
    ("Don't cry, snowman, don't leave me this way", 3.0),
    ("A puddle of water can't hold me close, baby", 3.5),
    ("Can't hold me close, baby", 2.0),
    ("", 1.0),
    ("I want you to know that I'm never leaving", 3.0),
    ("'Cause I'm Mrs. Snow, 'til death we'll be freezing", 3.0),
    ("Yeah, you are my home, my home for all seasons", 3.5),
    ("So come on, let's go", 2.0),
    ("Let's go below zero and hide from the sun", 3.0),
    ("I'll love you forever where we'll have some fun", 3.0),
    ("Yes, let's hit the North Pole and live happily", 3.5),
    ("Please don't cry no tears now, it's Christmas, baby", 4.0),
    ("", 1.0),
    ("My snowman and me, eh", 2.5),
    ("My snowman and me", 2.0),
    ("Baby", 1.5)
]

def strip_ansi(s):
    return re.sub(r'\033\[.*?m', '', s)

def draw_tree_and_lyric(lyric_line=""):
    os.system('cls' if os.name == 'nt' else 'clear')
    print()

    # Star
    star_line_content = ' ' * (WIDTH // 2) + YELLOW + '★' + RESET
    star_line_visible_width = len(strip_ansi(star_line_content))
    padding = ' ' * (WIDTH + SEPARATOR_WIDTH - star_line_visible_width)
    print(f"{star_line_content}{padding}{lyric_line if lyric_line else ''}")

    # Tree branches and trunk
    tree_body_height = HEIGHT + 3
    for i in range(1, tree_body_height):
        if i < HEIGHT:
            branch_width = i if i % 2 != 0 else i -1
            branch = ''.join([random.choice(ALL_COLORS) + '●' + GREEN if random.random() < 0.2 else '▲' for _ in range(branch_width)])
            tree_line_content = ' ' * ((WIDTH - branch_width) // 2) + GREEN + branch + RESET
        else:
            trunk_width = HEIGHT // 4
            tree_line_content = ' ' * ((WIDTH - trunk_width) // 2) + WHITE + '█' * trunk_width + RESET
        
        tree_line_visible_width = len(strip_ansi(tree_line_content))
        padding = ' ' * (WIDTH + SEPARATOR_WIDTH - tree_line_visible_width)
        print(f"{tree_line_content}{padding}")

    # Message
    message_line_content = '\n' + ' ' * ((WIDTH - 15) // 2) + RED + 'Merry Christmas!' + RESET
    print(message_line_content)
    print()


def animate_lyrics():
    try:
        for lyric, duration in LYRICS_TIMINGS:
            draw_tree_and_lyric(lyric)
            time.sleep(duration)
        draw_tree_and_lyric()
    except KeyboardInterrupt:
        print("\nAnimation stopped. Merry Christmas!")

if __name__ == "__main__":
    animate_lyrics()
