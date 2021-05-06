﻿from decorators import commands
import random
from core import GetSavedEmojis
from shizu_tasks import *
from shizu_database import ShizuDatabase
from discord import File
import requests
from bot_vars import SHIZUWEB

ip = requests.get('https://checkip.amazonaws.com').text.strip()


class ShizuCommands:
    
    def __init__(self, shizu):
        self.shizu = shizu
        self.shizu_tasks = shizu.shizu_tasks
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
        loop_times = 0

        if len(splitted) > 1:
            loop_times = int(splitted[1])
        
        message.content = ";emoji"
        # Obtengo o creo el documento de la DB
        task_doc = self.shizu.shizu_document.create_task_document("emoji", "time_task", message, minutes_until_execute, loop_times)
        # Actualizo o guardo por primera vez el documento en la DB
        database_task_id = self.shizu.database.save_task(task_doc)
        if not database_task_id:
            await message.channel.send("Hubo un error al guardar la tarea en la base de datos, abortando.")
            return print("ERROR AL GUARDAR LA TASK EN LA BASE DE DATOS!!")

        # creo la task para que comience a ejecutarse
        self.shizu.shizu_tasks.start_task(task_doc)

        discord_reply = f"Ok, cada {minutes_until_execute} minutos posteare un emoji"
        discord_reply += "." if loop_times == 0 else f" con un total de {loop_times} veces."
        await message.channel.send(discord_reply)
            
    @commands()
    async def web(self, message):
        msg = "WEB en proceso: http://"+SHIZUWEB+"/ \nWEB vieja: http://"+ip+"/"
        await message.channel.send(msg)

    @commands()
    async def exp(self, message):
        author = message.author
        doc = {
            "_id" : author.id
        }
        current_exp = round(self.database.get_document("members", doc)["experience"])
        level = self.database.get_document("members", doc)["level"]
        current_lvl_exp = round(self.database.get_lvl_experience(level))
        next_lvl_exp = round(self.database.get_lvl_experience(level + 1))
        lvl_exp = abs(next_lvl_exp - current_lvl_exp) 

        # experiencia obtenida en el nivel actual, ej: lvl 15 con 12321/40000 de exp para nivel 16
        actual_lvl_exp = abs( (current_exp - current_lvl_exp) + lvl_exp)

        await message.channel.send(f"Level {level}. Experiencia {actual_lvl_exp}/{lvl_exp}.")

    @commands()
    async def birthday(self, message):
        await message.channel.send("Nací en 2016-04-25 21:39:58 -0300")

    @commands()
    async def choose(self, message):
        words = message.content.split(',')
        if len(words) > 1:
            await message.channel.send(random.choice(words))
        else:
            await message.channel.send("Formato invalido ==> escribe: ;choose opcion1, opcion2, etc")

    @commands()
    async def remind(self, message):
        command = message.content
