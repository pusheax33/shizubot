import inspect


class CommandList:
    command_list = []

    @classmethod
    def add_command(cls, func):
        if inspect.isfunction(func) or inspect.ismethod(func):
            if func not in cls.command_list:
                print(f"La funcion {func.__name__} fue agregada como comando.")
                cls.command_list.append(func)

    @classmethod
    def get_command_list(cls):
        return cls.command_list
