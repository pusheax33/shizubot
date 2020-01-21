from decorators import *
import os
import random
from image_download import googleimagesdownload
from core import debug_log, GetSavedEmojis
from shizu_tasks import *

class ShizuCommands():

    def __init__(self):
        self.image_downloader = googleimagesdownload()
        self.shizu_tasks = ShizuTasks()
        self.helper = ShizuCommandsHelper(self)


    @commands(prefix="ayuda")
    async def help(self, message):
        await message.channel.send("```Comandos:\nhelp, ping, join, say, img, gif, yt, play```")

    @commands()
    async def ping(self, message):
        await message.channel.send("pong")

    @commands(prefix = 'decir')
    async def say(self, message):
        if message.content == "": return
        async with message.channel.typing():
            await message.channel.send(message.content)

    @commands()
    async def ii(self, message):
        msg = message.content.replace('a', 'i').replace('e', 'i').replace('o', 'i').replace('u', 'i')
        await message.channel.send(msg)

    @commands()
    async def img(self, message):
        image_to_search = message.content
        image_position = random.randrange(0, 8)
        image_time = [None, "past-24-hours", "past-year", None, "past-7-days",
                      None, "past-7-days", None, "past-month", "past-month",
                      "past-month", None, "past-year", None, "past-year", "past-year"
                      ]

        image_type = ["png", "jpg"]

        arguments = {
                     "keywords": image_to_search,
                     "no_download": True,
                     "silent_mode": True,
                     "limit": image_position,
                     "safe_search": True,
                     "format": random.choice(image_type),
                     "offset": image_position
                     }

        choice = random.choice(image_time)
        if choice != None:
            arguments["time"] = choice

        debug_log(arguments)

        paths = self.image_downloader.download(arguments)
        image_url = paths[0][image_to_search][0]

        await message.channel.send(image_url)

    @commands()
    async def emoji(self, message):
        emojis = GetSavedEmojis()
        base=os.path.basename(random.choice(emojis))
        await message.channel.send(r"https://cdn.discordapp.com/emojis/" + base)

    @commands()
    async def postemoji(self, message):
        minutes = 60
        if (message.content):
            try:
                minutes = int(message.content)
                await message.channel.send("Ok, colocare un emoji cada " + str(minutes) + " minutos.")
            except:
                print("Formato invalido de mensaje, dejando los 60 minutos por defecto")

        self.shizu_tasks.create_task(minutes, self.helper.postemoji, message)

    @commands()
    async def stoptask(self, message):
        task_name = message.content

    @commands()
    async def debug(self, message):
        bot_vars.DEBUG = not bot_vars.DEBUG
        result = "Activado" if bot_vars.DEBUG == True else "Desactivado"
        await message.channel.send("Modo debug ahora esta " + result)

    @commands()
    async def task(self, message):
        self.shizu_tasks.create_task(1, message.channel.send, "yeass")

    @commands(prefix="recordartomaragua")
    async def waterdrinkreminder(self, message):
        self.shizu_tasks.create_task(4 * 60, message.channel.send, "Recuerda tomar tu awita!")

    @commands()
    async def gif(self, message):
        image_to_search = message.content
        gif_position = random.randrange(0, 8)
        image_time = [None, "past-year", None, None, "past-7-days", None,
                      "past-month", "past-month", "past-month", None,
                      "past-year", None, "past-year", "past-year"
                      ]
        arguments = {
                     "keywords": image_to_search,
                     "no_download": True,
                     "silent_mode": True,
                     "safe_search": True,
                     "limit": gif_position,
                     "format": "gif",
                     "offset": gif_position
        }
        choice = random.choice(image_time)
        if choice != None:
            arguments["time"] = choice

        debug_log(arguments)

        paths = self.image_downloader.download(arguments)
        image_url = paths[0][image_to_search][0]

        await message.channel.send(image_url)

# ==================================== COMANDOS IGNORADOS ======================================== #    
class ShizuCommandsHelper():

    def __init__(self, shizu_commands):
        self.shizu_commands = shizu_commands

    async def postemoji(self, message):
        # obtengo un emoji aleatorio y lo posteo
        message.content = ";emoji " + message.content
        await self.shizu_commands.emoji(message)