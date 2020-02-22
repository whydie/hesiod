import youtube_dl

from urllib.parse import urlparse
from urllib.parse import parse_qs

from utils import PlayerStatus
from config import TMP_NAME

from discord import FFmpegOpusAudio

PLAYLIST_MAX_SIZE = 5
YOUTUBE_PREFIX = "https://www.youtube.com/watch?v=%(video_id)s"


ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": TMP_NAME + "/%(display_id)s"
}


class Player:
    def __init__(self):
        self.playlist = []
        self.playing = False
        self.client = None

    def addSong(self, source: FFmpegOpusAudio):
        if len(self.playlist) < PLAYLIST_MAX_SIZE:
            self.playlist.append(FFmpegOpusAudio)
            return PlayerStatus.SUCCESS
        else:
            return PlayerStatus.FAILED

    def pause(self):
        pass

    def play(self):
        pass


class Youtube:
    @staticmethod
    def get_video(video: str):
        print(video)
        if video.find("?v=") == -1:
            print("hello")
            # video is video_id
            # build URL from given video_id
            url = YOUTUBE_PREFIX % {"video_id": video}
        else:
            # video is URL
            # remove every URL param except of "v" video id
            url = urlparse(video)
            params = parse_qs(url.query)
            url = YOUTUBE_PREFIX % {"video_id": params['v'][0]}
    
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            file = ydl.extract_info(url, download=True)

        return file["display_id"]

