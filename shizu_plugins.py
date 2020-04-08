import inspect
from shizu_commands import ShizuCommands
from shizu_music import ShizuMusic
from shizu_admin import ShizuAdmin
from shizu_media import ShizuMedia
from shizu_youtube import ShizuYoutube
from shizu_coronavirus import ShizuCoronaVirus
from shizu_images import ShizuImage


class ShizuPlugin:
    """
        Esta clase es un contenedor de clases que pueden tener comandos para el bot
        Para que el bot registre un comando debe agregarsele el decorador @commands
        y agregar la clase correspondiente a la lista de esta clase.
    """
    
    plugin_list = []

    def __init__(self, shizu):
        self.plugin_list = [
            ShizuCommands(shizu),
            ShizuMusic(shizu),
            ShizuAdmin(),
            ShizuMedia(shizu),
            ShizuYoutube(shizu),
            ShizuCoronaVirus(shizu),
            ShizuImage()
        ]

    def get_class(self, class_name):
        for cls in self.plugin_list:
            if cls.__class__.__name__ == class_name:
                return cls
