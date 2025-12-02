import os
import time
import random
import re
from typing import List, Tuple, Optional

# --- Configuration Constants ---

# Tree dimensions
HEIGHT = 20
WIDTH = 40  # Maximum width for the tree's content area (used for alignment)
SEPARATOR_WIDTH = 6  # Width of the gap between tree and lyrics

# The total number of lines the tree structure occupies (Star + Branches + Trunk)
TOTAL_TREE_BODY_LINES = 1 + (HEIGHT // 2) + 3
MAX_LYRIC_LINES = 15  # The total number of lines to display lyrics on screen

# Colors (ANSI escape codes)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[34m"
CYAN = "\033[96m"  # 水藍色 (Light Blue) for the border
MAGENTA = "\033[95m"
WHITE = "\033[97m"
RESET = "\033[0m"
ORANGE = "\033[38;5;208m"
GOLD = "\033[38;5;220m"
PINK = "\033[38;5;200m"

ALL_COLORS = [RED, YELLOW, BLUE, CYAN, MAGENTA, ORANGE, GOLD, PINK]

# Box drawing characters for lyrics frame (Solid Lines)
BOX_TOP_LEFT = "┌"
BOX_TOP_RIGHT = "┐"
BOX_BOTTOM_LEFT = "└"
BOX_BOTTOM_RIGHT = "┘"
BOX_HORIZONTAL = "─"
BOX_VERTICAL = "│"


# --- Utility Functions ---


def strip_ansi(s: str) -> str:
    """Removes ANSI escape codes from a string."""
    return re.sub(r"\033\[.*?m", "", s)


def parse_lrc(filepath: str) -> Tuple[str, str, List[Tuple[float, str]]]:
    """
    Parses an LRC file and returns a tuple of (song_title, artist, list of (timestamp_in_seconds, lyric) tuples).
    """
    lyrics_with_timestamps: List[Tuple[float, str]] = []
    song_title = "Unknown Song"
    artist = "Unknown Artist"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                artist_match = re.match(r"\[ar:(.*)\]", line)
                if artist_match:
                    artist = artist_match.group(1).strip()
                    continue

                title_match = re.match(r"\[ti:(.*)\]", line)
                if title_match:
                    song_title = title_match.group(1).strip()
                    continue

                match = re.match(r"\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)", line)
                if match:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    milliseconds = int(match.group(3).ljust(3, "0"))
                    timestamp = minutes * 60 + seconds + milliseconds / 1000
                    lyric = match.group(4).strip()
                    lyrics_with_timestamps.append((timestamp, lyric))
    except FileNotFoundError:
        print(
            f"Error: LRC file not found at '{filepath}'. Please make sure 'snowman_lyrics.lrc' is in the correct directory."
        )
        return (song_title, artist, [])

    return (song_title, artist, lyrics_with_timestamps)


# Load lyrics data once at startup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LRC_FILE_PATH = os.path.join(SCRIPT_DIR, "snowman_lyrics.lrc")
SONG_TITLE, ARTIST, LYRICS_TIMED = parse_lrc(LRC_FILE_PATH)

# Fixed frame width based on the longest lyric: 54 characters + 2 borders = 56
LYRICS_FRAME_WIDTH = 56
LYRICS_CONTENT_WIDTH = LYRICS_FRAME_WIDTH - 2


# --- Drawing Functions ---


def _get_tree_line_content(line_idx: int) -> str:
    """Generates the tree content (Star, Branch, or Trunk) for a given line index."""

    # 0: Star
    if line_idx == 0:
        return " " * ((WIDTH // 2) - 1) + YELLOW + "★" + RESET

    # 1 to TOTAL_TREE_BODY_LINES - 4: Branches
    elif line_idx >= 1 and line_idx <= TOTAL_TREE_BODY_LINES - 4:
        # i is the effective height index starting from 1
        i = (line_idx - 1) * 2 + 1

        branch_width = min(i, WIDTH)
        branch = ""
        for _ in range(branch_width):
            if random.random() < 0.2:
                branch += random.choice(ALL_COLORS) + "●" + GREEN
            else:
                branch += "▲"

        return " " * ((WIDTH - branch_width) // 2) + GREEN + branch + RESET

    # TOTAL_TREE_BODY_LINES - 3 to TOTAL_TREE_BODY_LINES - 1: Trunk
    elif line_idx >= TOTAL_TREE_BODY_LINES - 3 and line_idx < TOTAL_TREE_BODY_LINES:
        trunk_width = HEIGHT // 4
        return " " * ((WIDTH - trunk_width) // 2) + WHITE + "█" * trunk_width + RESET

    return ""


def _format_lyric_line(lyric: str) -> str:
    """Centers and pads a single lyric line to the content width."""
    lyric_width = len(strip_ansi(lyric))
    if lyric_width < LYRICS_CONTENT_WIDTH:
        padding_left = (LYRICS_CONTENT_WIDTH - lyric_width) // 2
        padding_right = LYRICS_CONTENT_WIDTH - lyric_width - padding_left
        # Use strip_ansi to separate content from color codes before padding
        centered_lyric = " " * padding_left + lyric + " " * padding_right
    else:
        centered_lyric = lyric[:LYRICS_CONTENT_WIDTH]

    # Ensure final string has correct visible width (e.g., if color codes were stripped)
    final_content = strip_ansi(centered_lyric)
    if len(final_content) < LYRICS_CONTENT_WIDTH:
        centered_lyric += " " * (LYRICS_CONTENT_WIDTH - len(final_content))

    return centered_lyric


def draw_tree(current_lyrics_list: List[str]):
    """Draws a shining Christmas tree with a scrolling list of lyrics."""

    os.system("cls" if os.name == "nt" else "clear")
    print()

    # --- 1. Prepare Lyrics Content ---
    formatted_title_text = f"《{SONG_TITLE}》 - {ARTIST}"
    # Title line is always YELLOW and centered
    title_line_content = YELLOW + _format_lyric_line(formatted_title_text) + RESET

    # Format and pad scrolling lyrics lines (always WHITE)
    white_lyrics = [WHITE + lyric + RESET for lyric in current_lyrics_list]
    
    available_content_lines = TOTAL_TREE_BODY_LINES - 2
    available_lyric_lines = available_content_lines - 1
    
    # Pad lyrics to fill remaining lines (excluding title line)
    empty_content_line = " " * LYRICS_CONTENT_WIDTH
    padded_lyrics_content = (
        [empty_content_line] * (available_lyric_lines - len(white_lyrics))
    ) + [_format_lyric_line(l) for l in white_lyrics]

    # Combine title and lyrics content
    all_content_lines = [title_line_content] + padded_lyrics_content

    # --- 2. Draw Top Border ---
    top_tree_line = _get_tree_line_content(0)
    top_tree_visible_width = len(strip_ansi(top_tree_line))
    
    # 修正凸出問題: 使用 WIDTH 來確保左邊界對齊
    # 填充 = 樹的最大寬度 + 分隔符寬度 - 該行樹的實際寬度
    top_padding = " " * (WIDTH + SEPARATOR_WIDTH - top_tree_visible_width)
    
    top_border = BOX_TOP_LEFT + BOX_HORIZONTAL * LYRICS_CONTENT_WIDTH + BOX_TOP_RIGHT
    # 邊框顏色改為 CYAN
    print(f"{top_tree_line}{top_padding}{CYAN}{top_border}{RESET}")

    # --- 3. Draw Content Lines ---
    for content_idx in range(available_content_lines):
        tree_line_idx = content_idx + 1
        tree_line_content = _get_tree_line_content(tree_line_idx)
        tree_line_visible_width = len(strip_ansi(tree_line_content))

        # 修正凸出問題: 使用 WIDTH 來確保左邊界對齊
        padding = " " * (WIDTH + SEPARATOR_WIDTH - tree_line_visible_width)
        
        content_line = all_content_lines[content_idx]
        
        # 邊框顏色改為 CYAN，確保顏色代碼只包圍邊界字符
        frame_line = f"{CYAN}{BOX_VERTICAL}{RESET}{content_line}{CYAN}{BOX_VERTICAL}{RESET}"
        print(f"{tree_line_content}{padding}{frame_line}")

    # --- 4. Draw Bottom Border ---
    bottom_tree_line_idx = TOTAL_TREE_BODY_LINES - 1
    bottom_tree_line = _get_tree_line_content(bottom_tree_line_idx)
    bottom_tree_visible_width = len(strip_ansi(bottom_tree_line))

    # 修正凸出問題: 使用 WIDTH 來確保左邊界對齊
    bottom_padding = " " * (WIDTH + SEPARATOR_WIDTH - bottom_tree_visible_width)
    
    bottom_border = BOX_BOTTOM_LEFT + BOX_HORIZONTAL * LYRICS_CONTENT_WIDTH + BOX_BOTTOM_RIGHT
    # 邊框顏色改為 CYAN
    print(f"{bottom_tree_line}{bottom_padding}{CYAN}{bottom_border}{RESET}")

    # 5. Draw Message
    message_line_content = (
        "\n" + " " * ((WIDTH - 15) // 2) + RED + "Merry Christmas!" + RESET
    )
    print(message_line_content)
    print()


# --- Main Animation Loop (Unchanged) ---


def animate():
    """Animates the shining tree and scrolling lyrics, synchronized with timestamps."""

    if not LYRICS_TIMED:
        print(
            "Running tree animation only (no synchronized lyrics) due to LRC file error."
        )
        available_content_lines = TOTAL_TREE_BODY_LINES - 2
        max_lyrics_lines = available_content_lines - 1
        while True:
            draw_tree([""] * max_lyrics_lines)
            time.sleep(0.1)

    start_time = time.time()
    next_lyric_index = 0
    available_content_lines = TOTAL_TREE_BODY_LINES - 2
    max_lyrics_lines = available_content_lines - 1
    visible_lyrics: List[str] = [""] * max(0, max_lyrics_lines - 3)

    try:
        while True:
            elapsed_time = time.time() - start_time

            # 1. Update Lyrics
            if (
                next_lyric_index < len(LYRICS_TIMED)
                and LYRICS_TIMED[next_lyric_index][0] <= elapsed_time
            ):
                new_lyric = LYRICS_TIMED[next_lyric_index][1]
                visible_lyrics.append(new_lyric)

                if len(visible_lyrics) > max_lyrics_lines:
                    visible_lyrics.pop(0)

                next_lyric_index += 1

            # 2. Draw Frame
            draw_tree(visible_lyrics)

            # 3. Time Control
            if next_lyric_index < len(LYRICS_TIMED):
                next_timestamp = LYRICS_TIMED[next_lyric_index][0]
                sleep_duration = next_timestamp - elapsed_time

                if sleep_duration > 0:
                    time.sleep(min(sleep_duration, 0.1))
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nAnimation stopped. Merry Christmas!")


if __name__ == "__main__":
    animate()