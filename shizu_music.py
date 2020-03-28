import asyncio
import discord
import youtube_dl
from decorators import commands
from functools import wraps

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

def ignorecalls():

    def decor(func):

        @wraps(func)
        async def wrapper(self, message):
            if __name__ == "__main__":
                print("YEP")
                await func(self, message)
            else:
                print("call ignorada")
                return False

        return wrapper
    return decor

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


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = ytdl.prepare_filename(data)
        print(filename)
        return filename

    @classmethod
    async def get_youtube_url(cls, url):
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        print(data)
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        return "https://www.youtube.com/watch?v=" + data['id']


class ShizuMusic():

    def __init__(self, shizu):
        self.shizu = shizu
        self.voice_client = None

    @commands('j')
    async def join2(self, message):
        """Joins a voice channel"""
        if message.author.voice == None:
            return await message.channel.send("No estas conectado a un canal de voz!! (😡)")
                
        channel = message.author.voice.channel
        # si ya existe un cliente de voz me cambio de canal al canal requerido
        if self.voice_client is not None:
            return await self.voice_client.move_to(channel)

        # si no existe, creo el canal de voz tomando el canal de voz en el que esta el usuario que ejecuta el comando
        voice_channel = message.author.voice.channel
        self.voice_client = await voice_channel.connect()

    @commands()
    async def test2(self, message):
        print("ASD")


    @commands()
    async def playlocal(self, message):
        """Plays a file from the local filesystem"""
        await self.ensure_voice(message)

        query = message.content
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        self.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await message.channel.send('Reproduciendo: {}'.format(query))

    @commands('p')
    async def play2(self, message):
        """Plays from a url (almost anything youtube_dl supports)"""
        await self.ensure_voice(message)

        url = message.content

        async with message.channel.typing():
            player = await YTDLSource.from_url(url, loop=self.shizu.loop)
            self.voice_client.play(player, after=lambda e: print('Error: %s' % e) if e else None)

        await message.channel.send('Reproduciendo: {}'.format(player.title))

    @commands('yt')
    async def youtube(self, message):
        await self.ensure_voice(message)

        url = message.content
        youtube_url = await YTDLSource.get_youtube_url(url)
        await message.channel.send(youtube_url)

    @commands('stream')
    async def stream(self, message):
        """Streams from a url (same as yt, but doesn't predownload)"""
        await self.ensure_voice(message)

        url = message.content

        async with message.channel.typing():
            player = await YTDLSource.from_url(url, loop=self.shizu.loop, stream=True)
            self.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await message.channel.send('Reproduciendo: {}'.format(player.title))

    @commands('vol')
    async def volume(self, message):
        """Changes the player's volume"""
        await self.ensure_voice(message)

        volume = int(message.content) or ""
        if volume == "":
            await message.channel.send("😡 Formato incorrecto!! escribe ;volumen <numero> siendo <numero> un numero del 0 al 100.")
            return

        if self.voice_client is None:
            return await message.channel.send("No estoy conectada a un canal de voz. (😡😡)")

        self.voice_client.source.volume = volume / 100
        await message.channel.send("El volumen ahora es {}%".format(volume))

    @commands('l')
    async def leave(self, message):
        """Paro el bot, me desconecto de el canal de voz y seteo el voice client a none"""
        await self.ensure_voice(message)

        self.voice_client = None
        await self.voice_client.disconnect()

    @commands()
    async def stop(self, message):
        await self.ensure_voice(message)
        self.voice_client.stop()

    @ignorecalls()
    async def ensure_voice(self, message):
        if self.voice_client is None:
            print("ES NONE")
            if message.author.voice:
                await message.author.voice.channel.connect()
                self.voice_client = message.author.voice
            else:
                await message.channel.send("No estas conectado a un canal de voz!! (😡)")
                return
        elif self.voice_client.is_playing():
            self.voice_client.stop()