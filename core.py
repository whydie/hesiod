import os
import youtube_dl

from urllib.parse import urlparse, parse_qs

from utils import PlayerStatus, convert_mb
from config import TMP_NAME, TMP_PATH, VIDEO_MAX_SIZE

from discord import AudioSource

PLAYLIST_MAX_SIZE = 5
YOUTUBE_PREFIX = "https://www.youtube.com/watch?v=%(video_id)s"


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

class Player:
    def __init__(self):
        self.playlist = []
        self.current_song = None
        self.client = None

    def addSong(self, source: AudioSource) -> PlayerStatus:
        """Add song to playlist

        :source: AudiSource object that contains song
        :return: Status of the action. E.G. if playlist is full than it will return 'PlayerStatus.LIST_IS_FULL'
        """
        if len(self.playlist) < PLAYLIST_MAX_SIZE:
            self.playlist.append(source)

            return PlayerStatus.SUCCESSFULLY_ADDED
        else:
            return PlayerStatus.LIST_IS_FULL

    def play(self):
        if not self.current_song:
            self.current_song = self.playlist.pop()
                
        self.client.play(self.current_song, after=self.next_song)

    def stop(self):
        self.client.stop()

    def pause(self):
        self.client.pause()

    def resume(self):
        self.client.resume()

    def next_song(self, exc=None):
        """Change current song to the next one

        :return: Status of the action. E.G. if song was successfully skipped than it will return 'PlayerStatus.SONG_SKIPPED'
        """
        if exc:
            print(exc)
        else:
            if self.client.is_playing():
                # Player is playing
                self.stop()
            if len(self.playlist) != 0:
                # Playlist is not empty

                self.current_song = self.playlist.pop()
                self.play()
                return PlayerStatus.SONG_SKIPPED
            else:
                self.current_song = None
                return PlayerStatus.SONG_NOT_SKIPPED

class Youtube:
    def get_video_title(url: str) -> str:
        # Couldn't find. Request info from youtube
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            file = ydl.extract_info(url, download=False)

        return file["title"]

    def get_video(video: str) -> str:
        """Donwload and save video from youtube if it's not downloaded already
        
        :param video: Youtube video id or full URL
        :return: Path to downloaded video
        """

        if video.find("youtu") != -1:
            # video is URL
            # remove every URL param except of "v" video id
            url = urlparse(video)
            if video.find("youtube.com") != -1:
                params = parse_qs(url.query)
                video_id = params['v'][0]
            else:
                url_splitted = url.path.split("/")
                video_id = url_splitted[1]
            url = YOUTUBE_PREFIX % {"video_id": video_id}
        else:
            # video is video_id
            # build URL from given video_id
            video_id = video
            url = YOUTUBE_PREFIX % {"video_id": video_id}

        for file in os.listdir(TMP_PATH):
            # Try to find requested video among already downloaded
            if file == video_id:
                return os.path.join(TMP_PATH, file), Youtube.get_video_title(url)
    
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            file = ydl.extract_info(url, download=True)

        return os.path.join(TMP_PATH, file["display_id"]), file["title"]

