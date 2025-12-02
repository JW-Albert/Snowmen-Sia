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

# 內容總行數：頂部邊框(1) + 標題行(1) + 歌詞行數(MAX_LYRIC_LINES) + 底部邊框(1)
# 總共佔用樹的 TOTAL_TREE_BODY_LINES 行
# 確保總行數計算正確：MAX_LYRIC_LINES = TOTAL_TREE_BODY_LINES - 3 (減去頂部邊框、標題行、底部邊框)
MAX_LYRIC_LINES = TOTAL_TREE_BODY_LINES - 3 # 14 - 3 = 11 行歌詞

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
    """
    Generates the tree content (Star, Branch, or Trunk) for a given line index.
    Ensures the *visible* output width is always exactly WIDTH for stable alignment.
    """

    # 0: Star (for the top-border line)
    if line_idx == 0:
        content = YELLOW + "★" + RESET
        content_width = len(strip_ansi(content))
        # 置中星號並填充到 WIDTH 寬度
        padding_left = (WIDTH - content_width) // 2
        padding_right = WIDTH - content_width - padding_left
        return " " * padding_left + content + " " * padding_right

    # 1 to TOTAL_TREE_BODY_LINES - 4: Branches (for title line, lyric lines)
    elif line_idx >= 1 and line_idx <= TOTAL_TREE_BODY_LINES - 4:
        i = (line_idx - 1) * 2 + 1
        branch_width = min(i, WIDTH)
        branch = ""
        for _ in range(branch_width):
            if random.random() < 0.2:
                branch += random.choice(ALL_COLORS) + "●" + GREEN
            else:
                branch += "▲"
        
        content_width = branch_width
        padding_left = (WIDTH - content_width) // 2
        padding_right = WIDTH - content_width - padding_left
        return " " * padding_left + GREEN + branch + RESET + " " * padding_right

    # TOTAL_TREE_BODY_LINES - 3 to TOTAL_TREE_BODY_LINES - 1: Trunk (for lyric and bottom border lines)
    elif line_idx >= TOTAL_TREE_BODY_LINES - 3 and line_idx < TOTAL_TREE_BODY_LINES:
        trunk_width = HEIGHT // 4
        content = WHITE + "█" * trunk_width + RESET
        content_width = trunk_width
        
        padding_left = (WIDTH - content_width) // 2
        padding_right = WIDTH - content_width - padding_left
        return " " * padding_left + content + " " * padding_right

    return " " * WIDTH # Fallback to full width space


def _format_content_line(text: str, target_color: str) -> str:
    """Centers text to the content width and applies color."""
    
    visible_content = strip_ansi(text)
    padded_content = visible_content.center(LYRICS_CONTENT_WIDTH)
    
    # 應用目標顏色代碼，並用 RESET 包住
    return f"{target_color}{padded_content}{RESET}"


def draw_tree(current_lyrics_list: List[str]):
    """Draws a shining Christmas tree with a scrolling list of lyrics."""

    os.system("cls" if os.name == "nt" else "clear")
    print()

    # --- 1. Prepare Content ---
    
    # 標題行 (不捲動)
    formatted_title_text = f"{SONG_TITLE} - {ARTIST}"
    title_content_with_color = _format_content_line(formatted_title_text, YELLOW)

    # 歌詞行 (捲動)
    white_lyrics_content = [
        _format_content_line(lyric, WHITE) for lyric in current_lyrics_list
    ]
    
    # 填充空行
    empty_content_line = _format_content_line("", WHITE) 
    padded_lyrics_content = (
        [empty_content_line] * (MAX_LYRIC_LINES - len(white_lyrics_content))
    ) + white_lyrics_content
    
    # 樹的行索引計數器 (從 0 開始)
    tree_line_counter = 0


    # --- 2. Draw Top Border (Tree Line 0) ---
    top_tree_line = _get_tree_line_content(tree_line_counter)
    top_padding = " " * SEPARATOR_WIDTH
    
    top_horizontal_bar_count = LYRICS_CONTENT_WIDTH
    top_border = BOX_TOP_LEFT + BOX_HORIZONTAL * top_horizontal_bar_count + BOX_TOP_RIGHT
    
    print(f"{top_tree_line}{top_padding}{CYAN}{top_border}{RESET}")
    tree_line_counter += 1


    # --- 3. Draw Title Row (Tree Line 1) ---
    title_tree_line = _get_tree_line_content(tree_line_counter)
    title_padding = " " * SEPARATOR_WIDTH
    
    # 構造標題行的邊框
    title_frame_line = f"{CYAN}{BOX_VERTICAL}{RESET}{title_content_with_color}{CYAN}{BOX_VERTICAL}{RESET}"
    
    print(f"{title_tree_line}{title_padding}{title_frame_line}")
    tree_line_counter += 1


    # --- 4. Draw Lyric Content Rows (Tree Lines 2 to 2 + MAX_LYRIC_LINES - 1) ---
    
    for lyric_content in padded_lyrics_content:
        lyric_tree_line = _get_tree_line_content(tree_line_counter)
        lyric_padding = " " * SEPARATOR_WIDTH
        
        # 構造歌詞行的邊框
        lyric_frame_line = f"{CYAN}{BOX_VERTICAL}{RESET}{lyric_content}{CYAN}{BOX_VERTICAL}{RESET}"
        
        print(f"{lyric_tree_line}{lyric_padding}{lyric_frame_line}")
        tree_line_counter += 1


    # --- 5. Draw Bottom Border (Tree Line TOTAL_TREE_BODY_LINES - 1) ---
    
    # 確保我們使用樹的最後一行
    bottom_tree_line = _get_tree_line_content(TOTAL_TREE_BODY_LINES - 1)
    bottom_padding = " " * SEPARATOR_WIDTH
    
    bottom_horizontal_bar_count = LYRICS_CONTENT_WIDTH
    bottom_border = BOX_BOTTOM_LEFT + BOX_HORIZONTAL * bottom_horizontal_bar_count + BOX_BOTTOM_RIGHT
    
    print(f"{bottom_tree_line}{bottom_padding}{CYAN}{bottom_border}{RESET}")

    # 6. Draw Message
    message_line_content = (
        "\n" + " " * ((WIDTH - 15) // 2) + RED + "Merry Christmas!" + RESET
    )
    print(message_line_content)
    print()


# --- Main Animation Loop (MAX_LYRIC_LINES has been redefined) ---


def animate():
    """Animates the shining tree and scrolling lyrics, synchronized with timestamps."""

    if not LYRICS_TIMED:
        print(
            "Running tree animation only (no synchronized lyrics) due to LRC file error."
        )
        max_lyrics_lines = MAX_LYRIC_LINES
        while True:
            draw_tree([""] * max_lyrics_lines)
            time.sleep(0.1)

    start_time = time.time()
    next_lyric_index = 0
    max_lyrics_lines = MAX_LYRIC_LINES
    # Start with fewer blank lines so first lyric appears earlier
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