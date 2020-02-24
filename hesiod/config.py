import os

from enum import Enum

from hesiod.utils import convert_mb

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_NAME = "tmp"
TMP_PATH = os.path.join(APP_ROOT, TMP_NAME)
VIDEO_MAX_SIZE = 100
PLAYLIST_MAX_SIZE = 5
YOUTUBE_PREFIX = "https://www.youtube.com/watch?v=%(video_id)s"

class PlayerStatus(Enum):
    FIRST_ADDED = 1
    SUCCESSFULLY_ADDED = 2
    LIST_IS_FULL = 3
    LIST_IS_EMPTY = 4
    SONG_CHANGED = 5
    SONG_NOT_CHANGED = 6
    SONG_LAST_CHANGED = 7
    ALREADY_PLAYING = 8


# YouTube_DL settings
def too_big_hook(d):
    if d['status'] == 'downloading':
        total_size = convert_mb(d.get("total_bytes", d.get('total_bytes_estimate')))
        if total_size > VIDEO_MAX_SIZE:
            raise ValueError("File size is too large")

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": TMP_NAME + "/%(display_id)s",
    "progress_hooks": [too_big_hook]
}