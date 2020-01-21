import inspect
from shizu_commands import ShizuCommands
from shizu_music import ShizuMusic


class ShizuPlugin:
    """
        This class is a container of classes that have commands for the bot.
        Every class added in the plugin list should import decorators and add
        the @commands(prefix="name") tag to make the commands work property
    """

    plugin_list = []

    def __init__(self, shizu):
        self.plugin_list = [ShizuCommands(), ShizuMusic(shizu)]

    def add_plugin(self, obj):
        if inspect.isclass(obj):
            self.plugin_list.append(obj)
        else:
            print("the parameter is not an object")
