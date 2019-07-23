from decorators import commands


class ShizuMusic:
    @commands(prefix = 'w')
    async def join(self, message):
        # voice = message.channel.guild.voice_channels
        voice_channel = message.author.voice.channel
        if voice_channel == None:
            await message.channel.send("No estas en ningun canal de voz <.<")
        else:
            await voice_channel.connect()
            await message.add_reaction('👍')
