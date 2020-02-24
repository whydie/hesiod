import atexit
import os

from hesiod.utils import clear_folder
from hesiod.config import TMP_PATH
from hesiod.commands import bot


if __name__ == "__main__":
    atexit.register(clear_folder, TMP_PATH)

    try:
        bot.run(os.getenv("HESIOD_TOKEN", "error"))
    except KeyboardInterrupt:
        clear_folder(TMP_PATH)