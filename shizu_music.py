import discord
from decorators import commands, avoid_external_calls
from bot_vars import COMMAND_PREFIX
from shizu_youtube import YoutubeDownloadHelper
from shizu_playlist import ShizuPlaylist
import asyncio
import traceback

class ShizuMusic:

    def __init__(self, shizu):
        self.shizu = shizu
        self.ytdl = YoutubeDownloadHelper()
        self.shizu_playlist = ShizuPlaylist()

    @commands()
    async def join(self, message):
        # Obtengo el cliente de voz de la guild actual
        voice_client = await self.get_voice_client(message)
        result = await self.ensure_voice(message)
        if not result and message.author.voice:
            if message.author.voice.channel.id != voice_client.channel.id:
                # Canales de voz distinto, se mueve el bot al canal del caller.
                caller_v_c = message.author.voice.channel
                await voice_client.move_to(caller_v_c)

    @commands()
    async def stop(self, message):
        voice_client = await self.get_voice_client(message)
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()

    @commands()
    async def pause(self, message):
        voice_client = await self.get_voice_client(message)
        if voice_client:
            if voice_client.is_playing():
                return voice_client.pause()

        await message.channel.send("No estoy reproduciendo nada.")

    @commands()
    async def resume(self, message):
        voice_client = await self.get_voice_client(message)
        if voice_client:
            if voice_client.is_paused():
                return voice_client.resume()

        await message.channel.send("??")

    @commands()
    async def skip(self, message):
        # next_song = self.playlist.play_next(message.channel.id)
        message.content = COMMAND_PREFIX+"stop"
        await self.stop(message)
        await message.channel.send("Skipped")
        message.content = COMMAND_PREFIX+"play"
        await self.play(message)

    @commands()
    async def volume(self, message):
        pass

    @commands()
    async def dpl(self, message):
        self.shizu_playlist.remove(message.channel.guild.id)
        return await message.channel.send("ok")

    @commands()
    async def leave(self, message):
        voice_client = await self.get_voice_client(message)
        if voice_client:
            print(voice_client.is_connected())
            await voice_client.disconnect()
        else:
            await message.channel.send("No estoy conectada a ningun canal!")

    @commands()
    async def play(self, message):
        yt_search_text = message.content
        server_id = message.channel.guild.id
        audio_data = ""

        if not await self.ensure_voice(message):
            return print("Ignorando play")

        voice_client = await self.get_voice_client(message)

        print("playing? ", voice_client.is_playing())
        if voice_client.is_playing():
            # Hay una musica ya reproduciendose, procedo a agregar la data de la musica requerida a la playlist
            audio_data = await self.ytdl.search(yt_search_text)
            if not audio_data:
                return await message.channel.send("No pude encontrar el video requerido, ignorando.")

            # Agrego la playlist
            playlist = self.shizu_playlist.add(server_id, audio_data)
            song_position = len(playlist["tracklist"]) - 1
            return await message.channel.send(f"```La cancion {audio_data['title']} se agrego a la playlist.\n"
                                              f"Se reproducira dentro de {song_position} canciones.```")
        else:
            # No se esta reproduciendo musica, intento obtener el siguiente track de la playlist...
            audio_data = self.shizu_playlist.get_next_song(server_id)

            if audio_data:
                if not audio_data["filepath"]:
                    # Descargo la musica desde youtube
                    audio_data = await self.ytdl.search(audio_data["url"], download=True)
            else:
                if not yt_search_text:
                    return
                # Descargo la cancion y obtengo o creo playlist
                audio_data = await self.ytdl.search(yt_search_text, download=True)
                if not audio_data:
                    return await message.channel.send("No pude encontrar el video requerido, ignorando.")
                if audio_data["duration"] > 36120:
                    return await message.channel.send("El video es mayor a 10 horas, ignorando.")

                # Agrego la cancion actual a la playlist
                self.shizu_playlist.add(server_id, audio_data)

            ggmepg_pcm = discord.FFmpegPCMAudio(audio_data["filepath"])
            if not voice_client.is_playing():
                voice_client.play(ggmepg_pcm, after=lambda err : self.caltes(message, err))
                await message.channel.send(f"```Reproduciendo ahora: {audio_data['title']}.\nElegida por {message.author.name}```")
            else:
                playlist = self.shizu_playlist.get(server_id)
                song_position = len(playlist["tracklist"]) - 1
                return await message.channel.send(f"```La cancion {audio_data['title']} se agrego a la playlist.\n"
                                                  f"Se reproducira dentro de {song_position} canciones.```")

    @avoid_external_calls
    def caltes(self, message, err):
        if err:
            print("error", err)
        message.content = COMMAND_PREFIX+"play"
        coro = self.play(message)
        future = asyncio.run_coroutine_threadsafe(coro, self.shizu.loop)
        try:
            print("ejecutando play again")
            future.result()
        except:
            traceback.print_exc()

    @avoid_external_calls
    async def get_voice_client(self, message):
        voice_clients = self.shizu.voice_clients
        for voice_client in voice_clients:
            if voice_client.guild.id == message.channel.guild.id:
                return voice_client

        return None

    @avoid_external_calls
    async def ensure_voice(self, message):
        author_voice = message.author.voice
        voice_client = await self.get_voice_client(message)

        if voice_client is None:
            if author_voice:
                # Me conecto al canal del caller
                voice_channel = author_voice.channel
                await voice_channel.connect()
                return True
            else:
                await message.channel.send("No estas conectado a ningun canal de voz! ")
        else:
            if author_voice:
                # Si hay un cliente de voz y el usuario que ejecuto el comando esta en el mismo canal de voz, devuelvo
                if author_voice.channel.id == voice_client.channel.id:
                    return True # caller voice channel = bot voice channel => ejecuto comando
                else:
                    pass # caller voice channel != bot voice channel => ignoro
            else: # Si hay un cliente pero el que ejecuta el comando no esta en ningun canal, no hago nada
                await message.channel.send("No estas conectado a ningun canal de voz! ")
        return False
