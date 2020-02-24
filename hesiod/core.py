from hesiod.config import PlayerStatus, PLAYLIST_MAX_SIZE

from discord import AudioSource
from collections import deque


class Player:
    def __init__(self):
        self.playlist = deque()
        self.current_song = None
        self.client = None

    def add_song(self, source: AudioSource) -> PlayerStatus:
        """Add song to the playlist

        :source: AudiSource object that contains song
        :return: If playlist is full, then it will return 'PlayerStatus.LIST_IS_FULL', 'PlayerStatus.SUCCESSFULLY_ADDED' otherwise
        """
        if len(self.playlist) < PLAYLIST_MAX_SIZE:
            # Initialize 'current_song' with first added song
            if not self.current_song:
                self.current_song = source
            else:
                self.playlist.append(source)

            return PlayerStatus.SUCCESSFULLY_ADDED
        else:
            return PlayerStatus.LIST_IS_FULL

    def play(self, force=False):
        """Play current playlist. If it's already playing, then depends on 'force' flag

        :param force: If 'force' is 'True', then stops player before playing 
        :return: If 'force' is 'False', then returns 'PlayerStatus.ALREADY_PLAYING', nothing otherwise
        """
        if self.client.is_playing():
            if force:
                self.stop()
            else:
                return PlayerStatus.ALREADY_PLAYING

        self.client.play(self.current_song, after=self.play_next)

    def play_next(self, exc=None):
        """Play next song if there is next song"""
        if exc:
            print(exc)
        else:
            status = self._next_song()

            # Last song. Stop player
            if status == PlayerStatus.SONG_LAST_CHANGED:
                self.stop()
            
            # Not last song. Change to the next song
            elif status == PlayerStatus.SONG_CHANGED:
                self.play(force=True)
            
            return status

    def _next_song(self):
        """Change to the next song if playlist is not empty"""
        # Playlist is not empty
        if len(self.playlist) != 0:
            next_song = self.playlist.popleft()
            self.current_song = next_song
            return PlayerStatus.SONG_CHANGED

        # Playlist is empty
        else:
            # Last song. Return special status
            if self.current_song:
                empty_status = PlayerStatus.SONG_LAST_CHANGED
            else:
                empty_status = PlayerStatus.SONG_NOT_CHANGED

            self.current_song = None
            return empty_status

    def stop(self):
        self.client.stop()

    def pause(self):
        self.client.pause()

    def resume(self):
        self.client.resume()

