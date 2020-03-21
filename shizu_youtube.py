from decorators import commands
import asyncio
import discord
import youtube_dl
import random
import os
import shutil
import glob
from urllib.error import HTTPError
import requests

ip = requests.get('https://checkip.amazonaws.com').text.strip()

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
beforeArgs = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
ytdl.beforeArgs = beforeArgs

class YoutubeDownloadHelper:

    def my_hook(self, d):
        print("TEST")

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
        """data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        print("download youtube DATA: ", data)

        # Si force_download = True significa que esta funcion retornara informacion para que el bot
        # en discord, en caso de haber algo raro (como un video de 10 horas), responda en discord
        # pidiendo permisos para descargar videos grandes o playlistgrandes o algo raro (para evitar trolls.)
        if force_download:
            if 'entries' in data and download_playlist: # redundante pero significa que es playlist
                entries = data['entries']
                for data in entries:
                    duration = int(data['duration'])
                    if duration >= 3600:
                        print("DURATION DEL VID MAYOR A 1 HORA")
                        #return {"status" : "paused", "duration", duration}

            elif not download_playlist: # Link video directo sin playlist
                duration = int(data['duration'])
                if duration >= 3600:
                    # Devuelvo la duracion para que shizu me pregunte si debo descargar un video asi o me estan troleando
                    print("DURATION DEL VID MAYOR A 1 HORA")
                    #return {"status" : "paused", "duration", duration}
"""
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))
        return {"status": "OK", "path": directory_name}


class ShizuYoutube:

    def __init__(self, shizu):
        self.shizu = shizu

    @commands('ytd')
    async def ytdownload(self, message):
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

"""        success = False
        def check(m):
            success = False
            if m.content[0] == "s":
                files = glob.glob('youtube/video')
                for f in files:
                    os.remove(f)

                files = glob.glob('youtube/audio')
                for x in files:
                    os.remove(x)
                success = True

            return success

        await message.channel.send("⚠️ Se van a eliminar todos los videos y audios subidos, continuar? (responder 's' para si 'n' para cancelar) ⚠️", delete_after=30)
        try:
            success = await self.shizu.wait_for('message', check=check, timeout=30)
            print("ASDADASDSA")
        except asyncio.TimeoutError:
            return await message.channel.send("⚠️⚠️⚠️ Tiempo de espera agotado, perro. Cancelado. ⚠️⚠️⚠️")
        else:
            print(":o")
        if success:
            free_mem = str(round((shutil.disk_usage("/")[2]/1024)/1024))
            await message.channel.send("Listo <3. Memoria Libre: " + free_mem + " MB")
        else:
            await message.channel.send("Ok, no hago nada... Memoria Libre: " + free_mem + " MB")"""

