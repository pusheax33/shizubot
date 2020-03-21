import discord
import random
import inspect
from shizu_plugins import ShizuPlugin
from bot_vars import *
from ctypes.util import find_library
from shizu_tasks import *
#from commands import Commands
import asyncio
import Debug
import time
from shizu_database import ShizuDatabase
from core import debug_log

class Shizu(discord.Client):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shizu_plugins = ShizuPlugin(self)
        self.owner_channel = None
        self.shizu_tasks = ShizuTasks()
        self.shizu_db = ShizuDatabase()
        loop = asyncio.get_event_loop()
        loop.create_task(self.run_check_tasks())

    async def run_check_tasks(self):
        while(True):
            await self.shizu_tasks.check_tasks()
            debug_log("durmiendo 10 segundos antes de ejecutar siguiente check de tasks...", "shizu")
            await asyncio.sleep(10)

    def run(self, *args, **kwargs):
        self.loop.run_until_complete(self.start(*args, **kwargs))

    async def on_ready(self):
        self.owner_channel = self.get_guild(OWNER_SERVER_ID).get_channel(OWNER_SERVER_CHANNEL)
        game = discord.Game(";help")
        await self.change_presence(activity=game)

        print(datetime.now().minute.__str__() + ":" + datetime.now().second.__str__())
        ######################## DATABASE ########################

        # No se si esta forma de updatear es lenta o rapida, pero por ahora se utilizara asi.
        # Basicamente dejo que mongo verifique si el id existe, si no existe agrega la coleccion
        await self.run_pending_tasks()
        for guild in self.guilds:
            self.shizu_db.save_guild(guild)
            for member in guild.members:
                #print("miembro %s guardado" % member.name)
                self.shizu_db.save_user(member)

        ######################## FIN DATABASE ########################
        print(datetime.now().minute.__str__() + ":" + datetime.now().second.__str__())

        print(
            """
              ______ ______ ______ ______ ______ ______ ______ ______ ______
             |______|______|______|______|______|______|______|______|______|
              ______ ______ ______ ______ ______ ______ ______ ______ ______
             |______|______|______|______|______|______|______|______|______|
              / ____| |   (_)                              | |     | | |
             | (___ | |__  _ _____   _   _ __ ___  __ _  __| |_   _| | |
              \___ \| '_ \| |_  / | | | | '__/ _ \/ _` |/ _` | | | | | |
              ____) | | | | |/ /| |_| | | | |  __/ (_| | (_| | |_| |_|_|
             |_____/|_| |_|_/___|\__,_| |_|  \___|\__,_|\__,_|\__, (_|_)
                                                               __/ |
              ______ ______ ______ ______ ______ ______ ______|___/__ ______
             |______|______|______|______|______|______|______|______|______|
              ______ ______ ______ ______ ______ ______ ______ ______ ______
             |______|______|______|______|______|______|______|______|______|
            """
        )

    async def on_message(self, message):
        # Agrego experiencia al duenio del mensaje en caso de ser necesario
        await self.give_experience(message) 
        await self.save_message_to_db(message)
        
        if message.author == self.user:
            #return
            pass

        if message.author.bot and message.author != self.user:
            print("eliminando mensaje de un bot")
            msg = message
            await message.delete()
            await message.channel.send(message.content)

        msg = message.content

        print("[%s] %s" % (message.author, message.content))
        if not msg or not msg.startswith(COMMAND_PREFIX):
            return

        await self.call_commands(message)


    async def call_commands(self, message):
                # obtengo cada metodo de la clase de comandos y verifico si hay match de comandos.
        for plugin in self.shizu_plugins.plugin_list:
            for name, method in inspect.getmembers(plugin, predicate=inspect.ismethod):
                if name == "__init__":
                    continue

                call = await method(message)

                if call is not False:
                    print("llamando a %s" % method)
                    break
            else:
                # esto para que en caso de que suceda llamada brekee en todo el for anidado y no solo en el interior
                continue
            break
        

    async def give_experience(self, message):
        # TODO: Checkear si el comando de experiencia esta habilitado en el server antes de responder
        #     : Verificar que el usuario no spamee mensajes y suba de nivel, es decir, agregar un delay entre exp y exp por user
        #     - No agregar Exp cuando se usa comandos del bot
        if message.author.bot and message.author.id != bot_vars.BOT_ID: return

        doc = {"_id" : message.author.id}
        db_member = self.shizu_db.query("members", doc)
        current_message_time = datetime.now()
        previous_message_time = db_member["last_message_time"]
    
        should_add_exp = True
        # Para nuevos integrantes al comienzo el "last_message_time" es cero, por lo que primero verifico si no es cero
        if previous_message_time:
            should_add_exp = (abs(previous_message_time - current_message_time)).total_seconds() > 30 # pasaron 30 segs desde ultimo mensaje?

        if should_add_exp:
            member_message_count = db_member["message_count"]
            
            debug_log(f"Total mensajes: {member_message_count})", "shizu")
            experience_to_add = len(message.content) * 0.2 + member_message_count * 0.4 + 60
            lvlup = self.shizu_db.add_experience(message.author, experience_to_add)

            if lvlup:
                new_lvl = db_member["level"] + 1 # Al level "viejo" (de la query antes de subir de lvl) le sumo uno para evitar hacer dos querys
                await message.channel.send(message.author.mention + " Avanzaste a nivel " + str(new_lvl) + "!")
        else:
            debug_log(f"No se pudo agregar exp a {message.author.name} porque no paso el tiempo requerido entre mensaje y mensaje", "shizu")
            

    async def run_pending_tasks(self):
        # Obtengo el channel porque necesito el id del channel para saber donde enviar el mensaje del comando
        tasks = self.shizu_db.get_collection("tasks")
        if tasks:
            for task in tasks:
                # por cada task pendiente en la base de datos, procedo a renaudarlas
                channel = self.get_channel(task["channel_id"])
                message = await channel.fetch_message(task["message_id"])
                if not message:
                    print(f"ERROR , NO SE PUDO OBTENER EL MENSAJE!!")
                    continue

                message.content = task["command"]
                debug_log(f"Ejecutando la tarea con el comando {message.content}...", "shizu")
                await self.call_commands(message)
                

    async def save_message_to_db(self, message):
        # Guardo cada mensaje a la db de la guild, con un total de 50 messages por canal
        guild = self.shizu_db.query("guilds", {"_id" : message.guild.id})
        if not guild:
            raise Exception
        channels = guild["channels"]

        last_channel_msg = []
        for chan in channels:
            if chan["id"] == message.channel.id:
                last_channel_msg = chan["last_50_messages"]
                break

        if len(last_channel_msg) >= 50:
            # Elimino un mensaje por superar el limite de 50
            del last_channel_msg[0]
        last_channel_msg.append(message.id)
        update_doc = {
            "last_50_messages" : last_channel_msg
        }
        self.shizu_db.save_guild(message.guild, update_doc)
        debug_log(f"Mensaje guardado en la db exitosamente", "shizu")


while (True):
    try:
        print("iniciando shizu")
        shizu = Shizu()
        shizu.run(TOKEN)
    except Exception as e:
        print("Me rompi")
        with open('errorlog.txt', 'a+') as error_log:
            error_log.write("[datetime.now().__str__()] " + e)
        time.sleep(5000)
