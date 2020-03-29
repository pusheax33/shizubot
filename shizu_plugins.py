import inspect
from shizu_commands import ShizuCommands
from shizu_music import ShizuMusic
from shizu_admin import ShizuAdmin
from shizu_media import ShizuMedia
from shizu_youtube import ShizuYoutube
from shizu_images import ShizuImage
from shizu_coronavirus import ShizuCoronaVirus
from shizu_images import ShizuImage


class ShizuPlugin:
    """
        This class is a container of classes that have commands for the bot.
        Every class added in the plugin list should import decorators and add
        the @commands(prefix="name") tag to make the commands work correctly
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

    def add_plugin(self, obj):
        if inspect.isclass(obj):
            self.plugin_list.append(obj)
        else:
            print("the parameter is not an object")
