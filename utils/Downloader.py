
from utils.Config import Config
from requests_futures.sessions import FuturesSession
from utils.Logger import *
from utils.Singleton import Singleton
import asyncio
import functools

import os

import youtube_dl
import ffmpeg
import uuid


class Downloader(metaclass=Singleton):
    def init(self, ) -> None:
        self.config = Config()
        self.root = "songs//"

    def transcode(self, fileName, extension):
        inpFileName = f"{fileName}.{extension}"
        ffmpeg.input(inpFileName).output(
            f"{fileName}.raw",
            format="s16le",
            acodec="pcm_s16le",
            ac=2,
            ar="48k",
            loglevel="error",
        ).overwrite_output().run()
        os.remove(inpFileName)

    # Download song

    async def download_and_transcode_song(self, songUrl):
        try:
            fileName = uuid.uuid4()

            extension = "webm"
            options = {
                # PERMANENT options
                'format': 'bestaudio/best',
                # 'keepvideo': False,
                # 'outtmpl': f'{fileName}.*',
                # 'postprocessors': [{
                #     'key': 'FFmpegExtractAudio',
                #     'preferredcodec': 'mp3',
                #     'preferredquality': '320'
                # }],
                # 'noplaylist': True
            }

            with youtube_dl.YoutubeDL(options) as ydl:
                # mp3.download([songUrl])
                info_dict = ydl.extract_info(songUrl, download=False)
                audio_file = ydl.prepare_filename(info_dict)
                ydl.process_info(info_dict)
            if audio_file is None:
                return None
            os.rename(audio_file,  f"{fileName}.{extension}")

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, functools.partial(self.transcode, f"{fileName}", extension)
            )
            return f"{self.root}{fileName}.raw"
        except Exception as ex:
            logException(
                f"Error while downlaoding and transcoding : {ex}", True)
            return None
