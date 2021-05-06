from decorators import commands
import asyncio
import youtube_dl
import random
import os
import shutil
import requests

ip = requests.get('https://checkip.amazonaws.com').text.strip()


class YoutubeDownloadHelper:

    @classmethod
    async def search(self, search_string, download=False):
        hexdigits = "0123456789abcdef"
        random_digits = "".join([ hexdigits[random.randint(0,0xF)] for _ in range(16) ])
        directory_name = "voice/"

        ytdl_format_options = {
            'format': 'bestaudio/best',
            'outtmpl': directory_name + random_digits + "%(title)s.%(ext)s",
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'force-ipv4': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }
        before_args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
        ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
        ytdl.beforeArgs = before_args

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_string, download=download))
        if 'entries' not in data:
            return

        data = data['entries'][0]
        filepath = "" if not download else ytdl.prepare_filename(data)

        return_data = {
            "filepath" : filepath, "url": "http://www.youtube.com/watch?v="+data["id"], "title": data["title"],
            "duration" : data["duration"], "view_count" : data["view_count"]
        }
        print(return_data)
        return return_data

class ShizuYoutube:

    def __init__(self, shizu):
        self.shizu = shizu

    @commands('yt')
    async def youtube(self, message):

        url = message.content
        youtube_url = await YoutubeDownloadHelper.search(search_string=url)

        await message.channel.send(youtube_url["url"])
