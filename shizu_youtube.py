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
        # print(data)
        filepath = "" if not download else ytdl.prepare_filename(data)

        return_data = {
            "filepath" : filepath, "url": "http://www.youtube.com/watch?v="+data["id"], "title": data["title"],
            "duration" : data["duration"], "view_count" : data["view_count"]
        }
        print(return_data)
        return return_data

    @classmethod
    async def download(self, url, filetype="video", download_playlist=False, extension="mkv", force_download=False):
        hexdigits = "0123456789abcdef"
        random_digits = "".join([ hexdigits[random.randint(0,0xF)] for _ in range(16) ])
        directory_name = "youtube/video/" + random_digits if filetype == "video" else "youtube/audio/" + random_digits

        ytdl_format_options = {
            'format': 'bestaudio/best' if filetype == "audio" else "(bestvideo[ext=mp4])[height<=1080]+bestaudio/best[height<=1080]",
            'outtmpl': directory_name + "/%(title)s.%(ext)s",
            'restrictfilenames': True,
            'noplaylist': not download_playlist,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'force-ipv4': True,
            '-cookies': 'cookies.txt',
            'default_search': 'auto',
            'source_address': '0.0.0.0', 
        }
        if extension != "mkv":
            print("Video se convertira a ", extension)
            ytdl_format_options["postprocessors"] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': extension,  # one of avi, flv, mkv, mp4, ogg, webm
            }]

        beforeArgs = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "

        ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
        ytdl.beforeArgs = beforeArgs
        
        loop = asyncio.get_event_loop()

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))
        return {"status": "OK", "path": directory_name}


class ShizuYoutube:

    def __init__(self, shizu):
        self.shizu = shizu

    @commands('yt')
    async def youtube(self, message):

        url = message.content
        youtube_url = await YoutubeDownloadHelper.search(search_string=url)

        await message.channel.send(youtube_url["url"])

    @commands('ytd')
    async def dw(self, message):
        result = {"status" : ""}
        url = ""
        filetype = ""
        extension = "mkv"
        download_playlist = False
        line_commands = message.content.split(' ')

        if len(line_commands) > 0:
            filetype = "video" # Por defecto, si no se indica, el filetype sera video
            if len(line_commands) >= 1:
                url = line_commands[0]
            if len(line_commands) >= 2:
                filetype = line_commands[1]
            if len(line_commands) >= 3:
                download_playlist = False if (line_commands[2]).lower()[0] == "f" else True
            if len(line_commands) >= 4:
                extension = line_commands[3]
        else:
            await message.channel.send("Formato incorrecto, ingresa: ;ytdownload url tipoarchivo(audio o vid) true/false(true descarga la playlist completa, false no)")
        
        await message.channel.send("Ok, descargando uwu")
        while result["status"] != "OK":
            print("en while...")
            await asyncio.sleep(1)
            async with message.channel.typing():
                try:
                    print("descargando!: ", url, filetype, download_playlist)
                    result = await YoutubeDownloadHelper.download(url, filetype=filetype, download_playlist=download_playlist, extension=extension) # Devuelve path de carpetas de videos descargados.
                    print("result: ", result)
                    if result["status"] == "paused":
                        if result["duration"] > 3600:
                            pass # TODO: esto.

                except OSError as e:
                    free_mem = str(round((shutil.disk_usage("/")[2]/1024)/1024))
                    await message.channel.send("⚠️⚠️⚠️Me quede sin memoria, abortando!!⚠️⚠️⚠️\n Memoria libre: " + free_mem + "\nUtiliza ;ytclean para liberar algo de memoria!")

                except Exception as e:
                    print(e.__class__.__name__)
                    await message.channel.send("Ocurrio un error desconocido!! Abortando para evitar ban ip..")
                    return

        if result["status"] == "OK":
            await message.channel.send("Completado!! Link de archivos: http://"+ip+"/shizu/" + result["path"])

    @commands("ytclean")
    async def ytclean(self, message):
        for paths in ['youtube/audio', 'youtube/video']:
            files = os.listdir(paths)
            for f in files:
                print(f)
                if os.path.isdir(paths+"/"+f):
                    print("ASD")
                    shutil.rmtree(paths+"/"+f)


        free_mem = str(round((shutil.disk_usage("/")[2]/1024)/1024))
        await message.channel.send("Listo <3. Memoria Libre: " + free_mem + " MB")

