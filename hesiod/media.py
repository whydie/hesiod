import os
import youtube_dl

from urllib.parse import urlparse, parse_qs

from hesiod.utils import convert_mb
from hesiod.config import TMP_PATH, YOUTUBE_PREFIX, ydl_opts


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