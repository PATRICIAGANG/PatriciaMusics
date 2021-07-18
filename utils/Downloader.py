
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


ydl_opts = {
    "format": "bestaudio[ext=m4a]",
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}

ydl = YoutubeDL(ydl_opts)


def download(url: str) -> str:
    info = ydl.extract_info(url, False)
    duration = round(info["duration"] / 60)

    try:
        ydl.download([url])
    return path.join("downloads", f"{info['id']}.{info['ext']}")
