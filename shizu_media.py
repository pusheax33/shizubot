from PIL import Image, UnidentifiedImageError
from core import GetSavedEmojis, get_saved_images
from decorators import *
import random
import asyncio
from discord import File
from core import debug_log
from shizu_database import ShizuDatabase
from shizu_tasks import ShizuTasks

class ShizuMedia():

    def __init__(self):
        self.database = ShizuDatabase()
        self.shizu_tasks = ShizuTasks()


    @commands()
    async def emojicollage(self, message):
        cantX = 5
        cantY = 4
        background = Image.new('RGBA', (128*cantX, 128*cantY), (48, 125, 188, 255))
        emojis = GetSavedEmojis()
        images_path = []
        
        for i in range(0, cantX * cantY):
            path=random.choice(emojis)
            print(path)
            images_path.append(path)

        counterWidth = 0
        counterHeight = 0
        for path in images_path:
            try:
                image = Image.open(path)
            except UnidentifiedImageError:
                return print("ERROR AL OBTENER LA IMAGEN DEL PATH")
            image = image.resize((128, 128))
            offset = (128 * counterWidth, 128 * counterHeight)
            background.paste(image, offset)
            counterWidth = (counterWidth + 1) % cantX
            if counterWidth % cantX == 0:
                counterHeight += 1

        background.save("emoji_collage.png")
        await message.channel.send(file=File('emoji_collage.png'))


    @commands()
    async def loopemojicollage(self, message):
        splitted = message.content.split(" ")
        if not message.content:
            raise Exception
        
        minutes_until_execute = int(splitted[0])
        loop_times = 0 # infinitas veces por defecto se ejecutara el loop

        if len(splitted) > 1:
            loop_times = int(splitted[1])
        
        # guardo la task en la base de datos, previamente serializando la funcion sino no funca
        message.content = ";emojicollage " + message.content
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
        self.shizu_tasks.create_task(new_task_id, message.content, minutes_until_execute, loop_times, self.emojicollage, message)
        debug_log("Task creada exitosamente", "shizucommands")
        if not task_exists:
            reply = f"Ok, cada {minutes_until_execute} minutos colocare un collage de emojis" + (f" con un total de {loop_times} veces." if loop_times else ".")
            await message.channel.send(reply)


    @commands()
    async def randomimage(self, message):
        images = get_saved_images()
        path=random.choice(images)
        await message.channel.send(file=File(path))


    @commands()
    async def looprandomimage(self, message):
        splitted = message.content.split(" ")
        if not message.content:
            raise Exception
        
        minutes_until_execute = int(splitted[0])
        loop_times = 0 # infinitas veces por defecto se ejecutara el loop

        if len(splitted) > 1:
            loop_times = int(splitted[1])
        
        # guardo la task en la base de datos, previamente serializando la funcion sino no funca
        message.content = ";randomimage " + message.content
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
        self.shizu_tasks.create_task(new_task_id, message.content, minutes_until_execute, loop_times, self.randomimage, message)
        debug_log("Task creada exitosamente", "shizucommands")
        if not task_exists:
            reply = f"Ok, cada {minutes_until_execute} minutos colocare una imagen random robada de algun server" + (f" con un total de {loop_times} veces." if loop_times else ".")
            await message.channel.send(reply)

# ejecuto un comando de loop, por ejemplo ;loopemojicollage o ;emojicollage loop xveces
# Agrego en la base de datos que en la guild x, canal x, el usuario x agrego como tarea ;loopemojicollage
# Ejecuto la funcion create_task en donde le paso el diccionario de la task que acabo de crear en la base de datos
# Cada x tiempo el check task se ejecuta y ejecutara el comando en caso de ser el tiempo
# si lo ejecuta se debe restar looptimes en caso de que no sea infinito y actualizar el tiempo

