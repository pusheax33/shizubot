from decorators import *
from discord.errors import HTTPException, NotFound, Forbidden
import os
import sys

class ShizuAdmin:

    def __init__(self, shizu):
        self.shizu = shizu

    @commands()
    async def debug(self, message):
        bot_vars.DEBUG = not bot_vars.DEBUG
        result = "Activado" if bot_vars.DEBUG == True else "Desactivado"
        await message.channel.send("Modo debug ahora esta " + result)

    @commands('clean')
    async def clear(self, message):
        try:
            messages_to_delete = int(message.content) + 1
        except:
            return await message.channel.send("usa ;clear cantidadmensajes para eliminar (ej ;clear 10)")

        if messages_to_delete <= 1:
            return await message.channel.send("usa ;clear cantidadmensajes para eliminar (ej ;clear 10)")

        channel_id = message.channel.id
        guild_info = self.shizu.database.get_document("guilds", {"_id": message.guild.id})
        channels = guild_info["channels"]
        message_channel_info = {}

        for channel in channels:
            if channel["id"] == channel_id:
                message_channel_info = channel
                break

        counter = 0
        print(message_channel_info)
        messages = []
        no_deleted_msgs = []
        # Agrego a la lista messages la cantidad de mensajes que el que ejecuto el comando quiere eliminar.
        for msg_id in message_channel_info["last_50_messages"][::-1]:
            if counter < messages_to_delete:
                try:
                    messages.append(await message.channel.fetch_message(msg_id))
                    counter += 1
                except NotFound:
                    # el mensaje no existe pero esta en la db, lo agrego para eliminarlo de la db. 
                    no_deleted_msgs.append(msg_id)
            else:
                # Agrego a la lista los mensajes no eliminados, esto para luego actualizarlo en el documento
                # y poder ejecutar el metodo database.update_document sin cagarla.
                no_deleted_msgs.append(msg_id)

        guild_info["channels"][guild_info["channels"].index(message_channel_info)]["last_50_messages"] = no_deleted_msgs
        print(guild_info["channels"][guild_info["channels"].index(message_channel_info)]["last_50_messages"])


        # no uso delete_messages porque solo elimina mensajes que son hasta 14 dias old
        try:
            await message.channel.delete_messages(messages)
        except HTTPException:
            # Alguno de los mensajes que se quieren eliminar usando bulk son mas viejos que 14 dias, por lo que
            # lo elimino manualmente
            for msg in messages:
                try:
                    await msg.delete()
                except HTTPException:
                    continue
                except NotFound:
                    continue
                except Forbidden:
                    return await message.channel.send("No tengo los permisos para hacer eso!")
        except Forbidden:
            return await message.channel.send("No tengo los permisos para hacer eso!")
        except NotFound:
            return await message.channel.send("Ocurrio un error (NotFound)")

        counter2 = len(messages)
        await message.channel.send(f"Listo!! {counter2} mensajes eliminados.", delete_after=10)

        # Elimino los mensajes eliminados de la base de datos
        self.shizu.database.update_document("guilds", guild_info)

