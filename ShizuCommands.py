from decorators import commands
import os
from chatter import *
import random
from chatterbot.conversation import Statement
from image_download import googleimagesdownload
from core import debug_log

class ShizuCommands:

    def __init__(self, shizu):
        self.shizu = shizu
        self.chatter = Chatter()
        self.image_downloader = googleimagesdownload()


    @commands(prefix="ayuda")
    async def help(self, message):
        await message.channel.send("```Comandos:\nhelp, ping, join, updatewords, say, img, gif, yt, play```")

    @commands()
    async def ping(self, message):
        await message.channel.send("pong")

    @commands()
    async def updatewords(self, message):
        path = "guilds/"
        feedback = ""
        file_counter = 0
        server_counter = 0
        already_server_added = False # variable que utilizo para contar de cuantos servers se aprende
        brain_previous_size = os.stat('db.sqlite3').st_size / 1024

        if not os.path.exists(path):
            await self.shizu.owner_channel.send("no existe la carpeta guilds/")
            return

        for dir in os.scandir(path):
            file_folder = path + dir.name
            print("file folder: " , file_folder)
            if os.path.isdir(file_folder):

                for file in os.scandir(file_folder):
                    file_path = path + dir.name + "/" + file.name
                    print("file path", file_path)
                    if os.path.isfile(file_path):
                        self.chatter.shizu_train(file_path)

                        # verifico si ya sume el contador de server para los archivos de loop actual
                        if not already_server_added:
                            already_server_added = True
                            server_counter += 1

                        file_counter += 1
                    else:
                        print("Si la ejecucion llega hasta este punto, significa que toda esta pila de basura que escribi no funciona.")
                        print("no es un archivo")

            already_server_added = False

        brain_updated_size = os.stat('db.sqlite3').st_size / 1024
        feedback += "```Total archivos aprendidos: %s de un total de %s servidores" % (str(file_counter), str(server_counter))
        feedback += "\nMi database pesaba antes: %s KB" % str(brain_previous_size)
        feedback += "\nMi database ahora pesa: %s KB```" % str(brain_updated_size)

        await self.shizu.owner_channel.send(feedback)
        await message.add_reaction('👍')

    @commands(prefix = 'decir')
    async def say(self, message):
        async with message.channel.typing():
            await message.channel.send(message.content)

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
