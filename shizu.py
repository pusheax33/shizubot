import discord
import random
import inspect
from ShizuCommands import *
from bot_vars import *
from ctypes.util import find_library

class Shizu(discord.Client):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cmd = ShizuCommands(self)
        self.owner_channel = None

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
        game = discord.Game("<3")
        await self.change_presence(activity=game)

    async def on_message(self, message):
        if message.author == self.user:
            return

        msg = message.content

        print("[%s] %s" % (message.author, message.content))
        if not msg or not msg.startswith(COMMAND_PREFIX):
            return

        # obtengo cada metodo de la clase de comandos y verifico si hay match de comandos.
        for name, method in inspect.getmembers(self.cmd, predicate=inspect.ismethod):
            if name == "__init__":
                continue

            call = await method(message)

            if call is not False:
                print("llamando a %s" % method)
                break


shizu = Shizu()

shizu.run(TOKEN)
