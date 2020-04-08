from discord.ext import commands


class Test(commands.Cog):

    def testo(self):
        return "cls(what)"


Test().testo()
