import os, shutil

from enum import Enum
from config import TMP_PATH


class PlayerStatus(Enum):
    FIRST_ADDED = 1
    SUCCESSFULLY_ADDED = 2
    LIST_IS_FULL = 3
    LIST_IS_EMPTY = 4
    SONG_SKIPPED = 5
    SONG_NOT_SKIPPED = 6

def clear_tmp():
    folder = TMP_PATH
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def convert_mb(bytes: int) -> int:
    # Converts bytes to mb
    kb = (bytes // 1024)
    return  kb // 1024