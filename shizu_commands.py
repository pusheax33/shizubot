from decorators import commands
import os
import random
from image_download import googleimagesdownload
from core import debug_log, GetSavedEmojis
from shizu_tasks import *
from shizu_database import ShizuDatabase
from discord import File, Embed
import pickle
import requests

ip = requests.get('https://checkip.amazonaws.com').text.strip()

class ShizuCommands():
    
    def __init__(self):
        self.image_downloader = googleimagesdownload()
        self.shizu_tasks = ShizuTasks()
        self.database = ShizuDatabase()
        self.instance = self


    @commands(prefix="ayuda")
    async def help(self, message):
        await message.channel.send("```Comandos:\nhelp, ping, join/leave, say, img, gif, yt, ytdownload, ytclean, play, postemoji, exp,```")

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
                     "safe_search": False,
                     "format": random.choice(image_type),
                     "offset": image_position
                     }

        choice = random.choice(image_time)
        if choice != None:
            arguments["time"] = choice

        debug_log(arguments)

        paths = self.image_downloader.download(arguments)
        try:
            image_url = paths[0][image_to_search][0]
            await message.channel.send(image_url)
        except:
            await message.channel.send("No pude encontrar nada >.<")


    @commands()
    async def emoji(self, message):
        emojis = GetSavedEmojis()
        path=random.choice(emojis)
        await message.channel.send(file=File(path))

    @commands()
    async def loopemoji(self, message):
        bot_vars.DEBUG_MESSAGE_FILTER = "shizucommands"
        splitted = message.content.split(" ")
        if not message.content:
            raise Exception
        
        minutes_until_execute = int(splitted[0])
        loop_times = 0 # infinitas veces por defecto se ejecutara el loop

        if len(splitted) > 1:
            loop_times = int(splitted[1])
        
        # guardo la task en la base de datos, previamente serializando la funcion sino no funca
        message.content = ";emoji " + message.content
        command_name = message.content.split(' ')[0]

        # Para el caso donde el user llame al comando y ya exista en la db la task verifico primero si esta en la db
        # teniendo en cuenta que debe haber un solo comando igual por cnal
        doc = {
            "channel_id" : message.channel.id,
            "command" : message.content
        }
        task_exists = self.database.query("tasks", doc) != None
        print(f"taskexists {task_exists}")

        if task_exists:
            # Elimino la task previa y agrego una nueva
            removed = self.database.remove("tasks", doc)
            print(f"La tarea fue removida???? {removed.deleted_count}")
            debug_log(f"Una tarea fue eliminada para volver a crear la misma tarea pero actualizada", "shizucommands")
            if not removed: # ???????
                raise Exception

        # Si no existe la task creo una nueva
        new_task_id = self.database.save_task(message, minutes_until_execute, loop_times)

        if not new_task_id: # ???????????
            raise Exception

        # creo la task para que comience a ejecutarse
        self.shizu_tasks.create_task(new_task_id, message.content, minutes_until_execute, loop_times, self.emoji, message)
        debug_log("Task creada exitosamente", "shizucommands")
        if not task_exists:
            reply = f"Ok, cada {minutes_until_execute} minutos colocare un emoji" + (f" con un total de {loop_times} veces." if loop_times else ".")
            await message.channel.send(reply)
            
    @commands()
    async def web(self, message):
        await message.channel.send("http://"+ip+"/")

    @commands()
    async def exp(self, message):
        author = message.author
        doc = {
            "_id" : author.id
        }
        current_exp = round(self.database.query("members", doc, "experience"))
        level = self.database.query("members", doc, "level")
        current_lvl_exp = round(self.database.get_lvl_experience(level))
        next_lvl_exp = round(self.database.get_lvl_experience(level + 1))
        lvl_exp = abs(next_lvl_exp - current_lvl_exp) # exp total para el siguiente nivel, ej: 40000

        actual_lvl_exp = abs( (current_exp - current_lvl_exp) + lvl_exp) # experiencia obtenida en el nivel actual, ej: lvl 15 con 12321/40000 de exp para nivel 16

        await message.channel.send(f"Level {level}. Experiencia {actual_lvl_exp}/{lvl_exp}.")


    @commands()
    async def perfil(self, message):
        await message.channel.send("Comando incompleto >.<")

    @commands()
    async def shop(self, message):
        await message.channel.send("Comando incompleto >.<")

    @commands()
    async def shizy(self, message):
        shizy = self.database.query("members", message.author.id, "shizy")
        await message.channel.send("Tenes un total de %d Shizys. ;shop para gastarlos" % shizy)


    @commands()
    async def stoptask(self, message):
        task_name = message.content

    @commands()
    async def birthday(self, message):
        await message.channel.send("Nací en 2016-04-25 21:39:58 -0300")


    @commands()
    async def gif(self, message):
        image_to_search = message.content

        image_position = random.randrange(0, 8)
        image_time = [None, "past-24-hours", "past-year", None, "past-7-days",
                      None, "past-7-days", None, "past-month", "past-month",
                      "past-month", None, "past-year", None, "past-year", "past-year"
                      ]

        arguments = {
                     "keywords": image_to_search,
                     "no_download": True,
                     "silent_mode": True,
                     "limit": image_position,
                     "safe_search": False,
                     "format": "gif",
                     "offset": image_position
                     }

        choice = random.choice(image_time)
        if choice != None:
            arguments["time"] = choice

        debug_log(arguments)

        paths = self.image_downloader.download(arguments)
        try:
            image_url = paths[0][image_to_search][0]
            await message.channel.send(image_url)
        except:
            await message.channel.send("No pude encontrar nada >.<")

    
    @commands()
    async def choose(self, message):
        words = message.content.split(',')
        if len(words) > 1:
            await message.channel.send(random.choice(words))
        else:
            await message.channel.send("Formato invalido ._. ==> escribe: ;choose opcion1, opcion2, etc")