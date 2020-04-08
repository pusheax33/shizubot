import discord
import inspect
import bot_vars
import asyncio
import time
from shizu_plugins import ShizuPlugin
from shizu_document import ShizuDocument
from shizu_tasks import ShizuTasks
from shizu_database import ShizuDatabase
from datetime import datetime
from core import debug_log
from commandlist import CommandList


class Shizu(discord.Client):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shizu_tasks = ShizuTasks(self)
        self.database = ShizuDatabase()
        self.shizu_document = ShizuDocument()
        self.shizu_plugins = ShizuPlugin(self)
        self.owner_channel = None
        loop = asyncio.get_event_loop()
        loop.create_task(self.run_check_tasks())

    async def run_check_tasks(self):
        while True:
            await self.shizu_tasks.check_tasks()
            debug_log("durmiendo 10 segundos antes de ejecutar siguiente check de tasks...", "shizu")
            await asyncio.sleep(10)

    def run(self, *args, **kwargs):
        self.loop.run_until_complete(self.start(*args, **kwargs))

    async def on_ready(self):
        self.owner_channel = self.get_guild(bot_vars.OWNER_SERVER_ID).get_channel(bot_vars.OWNER_SERVER_CHANNEL)
        game = discord.Game(";help")
        await self.change_presence(activity=game)

        print(datetime.now().minute.__str__() + ":" + datetime.now().second.__str__())

        ########################## DATABASE ##########################
        # No se si esta forma de updatear es lenta o rapida, pero por ahora se utilizara asi.
        # Basicamente dejo que mongo verifique si el id existe, si no existe agrega la coleccion
        await self.run_pending_tasks()
        for guild in self.guilds:
            guild_doc = self.shizu_document.create_guild_document(guild)
            self.database.save_guild(guild_doc)

            for member in guild.members:
                #print("miembro %s guardado" % member.name)
                member_doc = self.shizu_document.create_user_document(member)
                self.database.save_member(member_doc)
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

        msg = message.content

        print("[%s] %s" % (message.author, message.content))
        if not msg or not msg.startswith(bot_vars.COMMAND_PREFIX):
            return

        await self.call_commands(message)

    async def call_commands(self, message):
        # obtengo cada metodo de la clase de comandos y verifico si hay match de comandos.
        for plugin in self.shizu_plugins.plugin_list:
            for name, method in inspect.getmembers(plugin, predicate=inspect.ismethod):
                if name == "__init__":
                    continue

                if inspect.iscoroutinefunction(method):
                    call = await method(message)
                else:
                    call = method(message)

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
        db_member = self.database.get_document("members", doc)
        current_message_time = datetime.now()
        previous_message_time = db_member["last_message_time"]
    
        should_add_exp = True
        # Para nuevos integrantes al comienzo el "last_message_time" es cero, por lo que primero verifico si no es cero
        if previous_message_time:
            should_add_exp = (abs(previous_message_time - current_message_time)).total_seconds() > 30 # pasaron 30 segs desde ultimo mensaje?

        if should_add_exp:
            member_message_count = db_member["message_count"]
            # TODO: LA EXP ESTA ROTA POR ALGUN MOTIVO, EL LAST_MESSAGE_TIME SE ACTUALIZA EN LA DB PERO NO INCREMENTA LA EXP
            
            debug_log(f"Total mensajes: {member_message_count})", "shizu")
            experience_to_add = len(message.content) * 0.2 + member_message_count * 0.4 + 60
            lvlup = self.database.add_experience(message.author, experience_to_add)

            # Guardo el tiempo del mensaje del usuario en la DB
            if db_member:
                db_member["last_message_time"] = datetime.now()
                saved = self.database.update_document("members", db_member)
                if not saved:
                    print("save_message_to_db: ERROR al guardar el tiempo actual en un usuario")

            if lvlup:
                new_lvl = db_member["level"] + 1 # Al level "viejo" (de la query antes de subir de lvl) le sumo uno para evitar hacer dos querys
                await message.channel.send(message.author.mention + " Avanzaste a nivel " + str(new_lvl) + "!")
        else:
            debug_log(f"No se pudo agregar exp a {message.author.name} porque no paso el tiempo requerido entre mensaje y mensaje", "shizu")
            
    async def get_message(self, channel_id, message_id):
        channel = self.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        return message

    async def run_pending_tasks(self):
        # Obtengo el channel porque necesito el id del channel para saber donde enviar el mensaje del comando
        tasks = self.database.get_documents("tasks")
        if not tasks:
            return

        for task_container in tasks:
            # Llamo todas las tasks pendientes!
            self.shizu_tasks.start_task(task_container)

    async def save_message_to_db(self, message):
        # Guardo cada mensaje a la db de la guild, con un total de 50 messages por canal
        guild_document = self.database.get_document("guilds", {"_id" : message.guild.id})
        if not guild_document:
            raise Exception
        channels = guild_document["channels"]
        
        last_messages = []
        for chan in channels:
            if chan["id"] == message.channel.id:
                last_messages = chan["last_50_messages"]
                break

        if len(last_messages) >= 50:
            del last_messages[0]
        last_messages.append(message.id)
        self.database.update_document("guilds", guild_document)

        debug_log(f"Mensaje guardado en la db exitosamente", "shizu")


while True:
    print("iniciando shizu")
    shizu = Shizu()
    shizu.run(bot_vars.CHIZU_TOKEN)
    time.sleep(5000)
