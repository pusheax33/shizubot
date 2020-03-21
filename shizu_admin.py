from decorators import *

class ShizuAdmin():

    def __init__(self):
        pass


    @commands()
    async def debug(self, message):
        bot_vars.DEBUG = not bot_vars.DEBUG
        result = "Activado" if bot_vars.DEBUG == True else "Desactivado"
        await message.channel.send("Modo debug ahora esta " + result)


    @commands()
    async def clr(self, message):
        embed= Embed(title="asd", color=0xe24b9b)
        embed.add_field(name="undefined", value="undefined", inline=False)
        await message.channel.send(embed=embed)