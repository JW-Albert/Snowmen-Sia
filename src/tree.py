import os
import time
import random
import re

def parse_lrc(filepath):
    """Parses an LRC file and returns a list of (timestamp_in_seconds, lyric) tuples."""
    lyrics_with_timestamps = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            match = re.match(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)', line)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                milliseconds = int(match.group(3).ljust(3, '0')) # Pad to 3 digits
                timestamp = minutes * 60 + seconds + milliseconds / 1000
                lyric = match.group(4).strip()
                lyrics_with_timestamps.append((timestamp, lyric))
    return lyrics_with_timestamps

# Tree dimensions
HEIGHT = 20
WIDTH = 40
SEPARATOR_WIDTH = 12  # Width of the gap between tree and lyrics

# Colors (ANSI escape codes)
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

LYRICS_TIMED = parse_lrc('snowman_lyrics.lrc')

def strip_ansi(s):
    """Removes ANSI escape codes from a string."""
    return re.sub(r'\033\[.*?m', '', s)

def draw_tree(current_lyrics_list=None):
    """Draws a shining Christmas tree with a scrolling list of lyrics."""
    if current_lyrics_list is None:
        current_lyrics_list = []
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print()

    # The total number of lines taken by the tree
    total_tree_lines = 1 + (HEIGHT // 2) + 3 
    
    # Pad the lyrics list with empty strings to match the tree height
    padded_lyrics = ([""] * (total_tree_lines - len(current_lyrics_list))) + current_lyrics_list
    
    lyric_idx = 0

    # Star
    star_line_content = ' ' * (WIDTH // 2) + YELLOW + '★' + RESET
    star_line_visible_width = len(strip_ansi(star_line_content))
    padding = ' ' * (WIDTH + SEPARATOR_WIDTH - star_line_visible_width)
    print(f"{star_line_content}{padding}{padded_lyrics[lyric_idx]}")
    lyric_idx += 1

    # Tree branches
    for i in range(1, HEIGHT, 2):
        branch = ''
        for _ in range(i):
            if random.random() < 0.2:
                branch += random.choice(ALL_COLORS) + '●' + GREEN
            else:
                branch += '▲'
        
        tree_line_content = ' ' * ((WIDTH - i) // 2) + GREEN + branch + RESET
        tree_line_visible_width = len(strip_ansi(tree_line_content))
        lyric_line = padded_lyrics[lyric_idx] if lyric_idx < len(padded_lyrics) else ""
        padding = ' ' * (WIDTH + SEPARATOR_WIDTH - tree_line_visible_width)
        print(f"{tree_line_content}{padding}{lyric_line}")
        lyric_idx += 1


    # Trunk
    trunk_width = HEIGHT // 4
    for i in range(3):
        trunk_line_content = ' ' * ((WIDTH - trunk_width) // 2) + WHITE + '█' * trunk_width + RESET
        trunk_line_visible_width = len(strip_ansi(trunk_line_content))
        lyric_line = padded_lyrics[lyric_idx] if lyric_idx < len(padded_lyrics) else ""
        padding = ' ' * (WIDTH + SEPARATOR_WIDTH - trunk_line_visible_width)
        print(f"{trunk_line_content}{padding}{lyric_line}")
        lyric_idx += 1

    # Message
    message_line_content = '\n' + ' ' * ((WIDTH - 15) // 2) + RED + 'Merry Christmas!' + RESET
    # No lyrics next to the message, so just print the message
    print(message_line_content)
    print()


def animate():
    """Animates the shining tree and scrolling lyrics, synchronized with timestamps."""
    start_time = time.time()
    next_lyric_index = 0
    visible_lyrics = []
    MAX_LYRIC_LINES = 15 

    try:
        # Pre-populate with a few blank lines
        for _ in range(MAX_LYRIC_LINES -1):
            visible_lyrics.append("")

        while True:
            elapsed_time = time.time() - start_time
            
            # Check if it's time to show the next lyric
            if next_lyric_index < len(LYRICS_TIMED) and \
               LYRICS_TIMED[next_lyric_index][0] <= elapsed_time:
                
                new_lyric = LYRICS_TIMED[next_lyric_index][1]
                visible_lyrics.append(new_lyric)
                
                # Trim the list if it's too long
                if len(visible_lyrics) > MAX_LYRIC_LINES:
                    visible_lyrics.pop(0)

                next_lyric_index += 1
            
            draw_tree(visible_lyrics)

            # Determine sleep time
            if next_lyric_index < len(LYRICS_TIMED):
                next_timestamp = LYRICS_TIMED[next_lyric_index][0]
                sleep_duration = next_timestamp - elapsed_time
                if sleep_duration > 0:
                    time.sleep(min(sleep_duration, 0.1)) # Sleep until next lyric or for a short while
                else:
                    time.sleep(0.01) # Keep animation smooth if behind schedule
            else:
                # After last lyric, just refresh
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nAnimation stopped. Merry Christmas!")

if __name__ == "__main__":
    animate()
