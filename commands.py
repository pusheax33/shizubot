from decorators import *

class Commands:
    command_list = []

    def __init__(self):
        pass

    def register(self, func):
        """ Registro un nuevo comando """
        if (callable(func)):
            pass