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

    def __init__(self, shizu):
        self.database = ShizuDatabase()
        self.shizu = shizu
        self.shizu_tasks = shizu.shizu_tasks

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
        message.content = ";randomimage"
        command_name = ";randomimage"

        task_doc = self.shizu.shizu_document.create_task_document("randomimage", "time_task", message, minutes_until_execute, loop_times)

        # Si no existe la task creo una nueva
        new_task_id = self.database.save_task(task_doc)

        if not new_task_id: # ???????????
            await message.channel.send("[looprandomimage]: Hubo un error al crear la task, abortando.")
            return

        # creo la task para que comience a ejecutarse
        self.shizu_tasks.start_task(task_doc)
        reply = f"Ok, cada {minutes_until_execute} minutos colocare una imagen random robada de algun server" + (f" con un total de {loop_times} veces." if loop_times else ".")
        await message.channel.send(reply)

# ejecuto un comando de loop, por ejemplo ;loopemojicollage o ;emojicollage loop xveces
# Agrego en la base de datos que en la guild x, canal x, el usuario x agrego como tarea ;loopemojicollage
# Ejecuto la funcion create_task en donde le paso el diccionario de la task que acabo de crear en la base de datos
# Cada x tiempo el check task se ejecuta y ejecutara el comando en caso de ser el tiempo
# si lo ejecuta se debe restar looptimes en caso de que no sea infinito y actualizar el tiempo

