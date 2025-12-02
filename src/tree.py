import os
import time
import random
import re
from typing import List, Tuple, Optional

# --- Configuration Constants ---

# Tree dimensions
HEIGHT = 20
WIDTH = 40
SEPARATOR_WIDTH = 6  # Width of the gap between tree and lyrics

# The total number of lines the tree structure occupies (Star + Branches + Trunk)
# 1 (Star) + (HEIGHT // 2) (Branches) + 3 (Trunk) = 1 + 10 + 3 = 14
TOTAL_TREE_BODY_LINES = 1 + (HEIGHT // 2) + 3
MAX_LYRIC_LINES = 15  # The total number of lines to display lyrics on screen

# Colors (ANSI escape codes)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
RESET = "\033[0m"
ORANGE = "\033[38;5;208m"
GOLD = "\033[38;5;220m"
PINK = "\033[38;5;200m"

ALL_COLORS = [RED, YELLOW, BLUE, CYAN, MAGENTA, ORANGE, GOLD, PINK]

# Box drawing characters for lyrics frame
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
    Added robust error handling for File Not Found.
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

                # Extract artist from [ar:Artist] tag
                artist_match = re.match(r"\[ar:(.*)\]", line)
                if artist_match:
                    artist = artist_match.group(1).strip()
                    continue

                # Extract song title from [ti:Title] tag
                title_match = re.match(r"\[ti:(.*)\]", line)
                if title_match:
                    song_title = title_match.group(1).strip()
                    continue

                # Regex matches [MM:SS.mmm]Lyric
                match = re.match(r"\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)", line)
                if match:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    # Pad to 3 digits for milliseconds calculation
                    milliseconds = int(match.group(3).ljust(3, "0"))
                    timestamp = minutes * 60 + seconds + milliseconds / 1000
                    lyric = match.group(4).strip()
                    lyrics_with_timestamps.append((timestamp, lyric))
    except FileNotFoundError:
        print(
            f"Error: LRC file not found at '{filepath}'. Please make sure 'snowman_lyrics.lrc' is in the correct directory."
        )
        # Return default title, artist and empty list to allow the tree animation to run without lyrics
        return (song_title, artist, [])

    return (song_title, artist, lyrics_with_timestamps)


# Load lyrics data once at startup
# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LRC_FILE_PATH = os.path.join(SCRIPT_DIR, "snowman_lyrics.lrc")
SONG_TITLE, ARTIST, LYRICS_TIMED = parse_lrc(LRC_FILE_PATH)

# Fixed frame width based on the longest lyric: "Who'll catch your tears if you can't catch me, darling"
# Length: 54 characters, plus 2 for frame borders = 56
LYRICS_FRAME_WIDTH = 56


# --- Drawing Functions ---


def _get_tree_line_content(lyric_idx: int) -> str:
    """Generates the tree content (Star, Branch, or Trunk) for a given line index."""

    # 0: Star
    if lyric_idx == 0:
        return " " * ((WIDTH // 2) - 1) + YELLOW + "★" + RESET

    # 1 to TOTAL_TREE_BODY_LINES - 4: Branches
    elif lyric_idx >= 1 and lyric_idx <= TOTAL_TREE_BODY_LINES - 4:
        # i is the effective height index starting from 1
        i = (lyric_idx - 1) * 2 + 1

        # Ensure branch width stays within tree limits, increasing by 2 each step
        branch_width = min(i, WIDTH)

        branch = ""
        for _ in range(branch_width):
            if random.random() < 0.2:
                branch += random.choice(ALL_COLORS) + "●" + GREEN
            else:
                branch += "▲"

        return " " * ((WIDTH - branch_width) // 2) + GREEN + branch + RESET

    # TOTAL_TREE_BODY_LINES - 3 to TOTAL_TREE_BODY_LINES - 1: Trunk
    elif lyric_idx >= TOTAL_TREE_BODY_LINES - 3 and lyric_idx < TOTAL_TREE_BODY_LINES:
        trunk_width = HEIGHT // 4
        return " " * ((WIDTH - trunk_width) // 2) + WHITE + "█" * trunk_width + RESET

    return ""  # Should not happen for valid indices


def draw_tree(current_lyrics_list: List[str]):
    """Draws a shining Christmas tree with a scrolling list of lyrics."""

    os.system("cls" if os.name == "nt" else "clear")
    print()

    # 1. Format song title: 《Snowman》 - Sia (in yellow)
    formatted_title = f"《{SONG_TITLE}》 - {ARTIST}"
    # Add white color to all lyrics and center them
    white_lyrics = []
    for lyric in current_lyrics_list:
        # Center the lyric within the frame (excluding border characters)
        lyric_width = len(lyric)
        content_width = LYRICS_FRAME_WIDTH - 2  # Exclude left and right borders
        if lyric_width < content_width:
            padding_left = (content_width - lyric_width) // 2
            padding_right = content_width - lyric_width - padding_left
            centered_lyric = " " * padding_left + lyric + " " * padding_right
        else:
            # If lyric is too long, truncate it
            centered_lyric = lyric[:content_width]
        white_lyrics.append(WHITE + centered_lyric + RESET)

    # Title is always at the first content line, lyrics scroll below it
    # Available content lines = TOTAL_TREE_BODY_LINES - 2 (top and bottom borders take 1 line each)
    # Line 1 is for title, lines 2 to available_content_lines are for lyrics
    available_content_lines = TOTAL_TREE_BODY_LINES - 2
    content_width = LYRICS_FRAME_WIDTH - 2  # Exclude left and right borders
    # Center title text first, then add color codes
    centered_title_text = formatted_title.center(content_width)
    title_line = YELLOW + centered_title_text + RESET

    # Pad lyrics to fill remaining lines (excluding title line)
    available_lyric_lines = available_content_lines - 1
    # Create empty lines with proper width
    empty_line = " " * content_width
    padded_lyrics = (
        [empty_line] * (available_lyric_lines - len(white_lyrics))
    ) + white_lyrics

    # 4. Draw Tree Body and Lyrics with Frame
    # First, print the top border (using tree line 0)
    first_tree_line = _get_tree_line_content(0)
    first_tree_line_visible_width = len(strip_ansi(first_tree_line))
    top_padding = " " * (WIDTH + SEPARATOR_WIDTH - first_tree_line_visible_width)
    top_border = (
        BOX_TOP_LEFT + BOX_HORIZONTAL * (LYRICS_FRAME_WIDTH - 2) + BOX_TOP_RIGHT
    )
    print(f"{first_tree_line}{top_padding}{BLUE}{top_border}{RESET}")

    # Then draw content lines with vertical borders (using tree lines 1 to TOTAL_TREE_BODY_LINES-2)
    # Line 1 is for title, lines 2+ are for lyrics
    for content_idx in range(available_content_lines):
        tree_line_idx = content_idx + 1
        tree_line_content = _get_tree_line_content(tree_line_idx)
        tree_line_visible_width = len(strip_ansi(tree_line_content))

        # Calculate padding to align the lyric frame after the separator
        padding = " " * (WIDTH + SEPARATOR_WIDTH - tree_line_visible_width)

        if content_idx == 0:
            # First content line is always the title
            content_line = title_line
        else:
            # Other lines are lyrics (index 0 in padded_lyrics corresponds to content_idx 1)
            lyric_idx = content_idx - 1
            if lyric_idx < len(padded_lyrics):
                content_line = padded_lyrics[lyric_idx]
            else:
                # Empty line with proper width
                content_line = " " * content_width

        # Ensure content_line has the correct visible width
        content_line_visible_width = len(strip_ansi(content_line))
        if content_line_visible_width < content_width:
            # Add padding to the right (before RESET if present, or at the end)
            padding_needed = content_width - content_line_visible_width
            if RESET in content_line:
                # Insert padding before RESET
                content_line = content_line.replace(RESET, " " * padding_needed + RESET)
            else:
                # Add padding at the end
                content_line = content_line + " " * padding_needed

        # Content line with vertical borders (content_line now has correct visible width)
        frame_line = f"{BOX_VERTICAL}{content_line}{BOX_VERTICAL}"
        print(f"{tree_line_content}{padding}{BLUE}{frame_line}{RESET}")

    # Finally, print the bottom border (using tree line TOTAL_TREE_BODY_LINES-1)
    last_tree_line_idx = TOTAL_TREE_BODY_LINES - 1
    last_tree_line = _get_tree_line_content(last_tree_line_idx)
    last_tree_line_visible_width = len(strip_ansi(last_tree_line))
    bottom_padding = " " * (WIDTH + SEPARATOR_WIDTH - last_tree_line_visible_width)
    bottom_border = (
        BOX_BOTTOM_LEFT + BOX_HORIZONTAL * (LYRICS_FRAME_WIDTH - 2) + BOX_BOTTOM_RIGHT
    )
    print(f"{last_tree_line}{bottom_padding}{BLUE}{bottom_border}{RESET}")

    # 4. Draw Message
    message_line_content = (
        "\n" + " " * ((WIDTH - 15) // 2) + RED + "Merry Christmas!" + RESET
    )
    print(message_line_content)
    print()


# --- Main Animation Loop ---


def animate():
    """Animates the shining tree and scrolling lyrics, synchronized with timestamps."""

    if not LYRICS_TIMED:
        print(
            "Running tree animation only (no synchronized lyrics) due to LRC file error."
        )
        # If no lyrics, run a simple, continuous animation
        available_content_lines = TOTAL_TREE_BODY_LINES - 2
        max_lyrics_lines = available_content_lines - 1
        while True:
            draw_tree([""] * max_lyrics_lines)
            time.sleep(0.1)  # Smooth refresh rate

    start_time = time.time()
    next_lyric_index = 0
    # Available content lines = TOTAL_TREE_BODY_LINES - 2 (top and bottom borders)
    # Actual lyrics lines = available_content_lines - 1 (excluding title)
    available_content_lines = TOTAL_TREE_BODY_LINES - 2
    max_lyrics_lines = available_content_lines - 1
    # Start with fewer blank lines so first lyric appears earlier
    visible_lyrics: List[str] = [""] * max(0, max_lyrics_lines - 3)

    try:
        while True:
            elapsed_time = time.time() - start_time

            # 1. Update Lyrics
            # Check if it's time to show the next lyric
            if (
                next_lyric_index < len(LYRICS_TIMED)
                and LYRICS_TIMED[next_lyric_index][0] <= elapsed_time
            ):

                new_lyric = LYRICS_TIMED[next_lyric_index][1]
                visible_lyrics.append(new_lyric)

                # Trim the list to maintain max_lyrics_lines, creating the scroll effect
                if len(visible_lyrics) > max_lyrics_lines:
                    visible_lyrics.pop(0)

                next_lyric_index += 1

            # 2. Draw Frame
            draw_tree(visible_lyrics)

            # 3. Time Control (Determines sleep duration for synchronization)
            if next_lyric_index < len(LYRICS_TIMED):
                next_timestamp = LYRICS_TIMED[next_lyric_index][0]
                sleep_duration = next_timestamp - elapsed_time

                # Sleep exactly until the next lyric's timestamp, or for a short maximum to keep the tree shining
                if sleep_duration > 0:
                    # Keep a minimum sleep duration to prevent a tight loop if timestamps are very close
                    time.sleep(min(sleep_duration, 0.1))
                else:
                    # If behind schedule (sleep_duration <= 0), quickly move to the next frame
                    time.sleep(0.01)
            else:
                # After the last lyric, just refresh the shining tree smoothly
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nAnimation stopped. Merry Christmas!")


if __name__ == "__main__":
    animate()
