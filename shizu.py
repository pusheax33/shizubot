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

class Shizu(discord.Client):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shizu_plugins = ShizuPlugin(self)
        self.owner_channel = None
        self.shizu_tasks = ShizuTasks()
        loop = asyncio.get_event_loop()
        loop.create_task(self.run_check_tasks())

    async def run_check_tasks(self):
        while(True):
            await self.shizu_tasks.check_tasks()
            if bot_vars.DEBUG:
                Debug.log("durmiendo 10 segundos antes de ejecutar siguiente check de tasks...")
            await asyncio.sleep(10)

    def run(self, *args, **kwargs):
        self.loop.run_until_complete(self.start(*args, **kwargs))


    async def on_ready(self):
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
        self.owner_channel = self.get_guild(OWNER_SERVER_ID).get_channel(OWNER_SERVER_CHANNEL)
        game = discord.Game(";help")
        await self.change_presence(activity=game)

    async def on_message(self, message):
        if message.author == self.user:
            return

        msg = message.content

        print("[%s] %s" % (message.author, message.content))
        if not msg or not msg.startswith(COMMAND_PREFIX):
            return

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