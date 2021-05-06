from functools import wraps
import bot_vars
import inspect
import os
from commandlist import CommandList


def commands(prefix=None, additional_prefix=None):

    def decor(func):

        func_name = func.__name__
        print("Fun NAME: " + func_name)
        command_prefix = bot_vars.COMMAND_PREFIX
        command_name_list = [command_prefix + (prefix or func_name), command_prefix + (additional_prefix or func_name)]

        @wraps(func)
        async def wrapper(self, message, *args):
            current_command = message.content.split(maxsplit=1)[0]

            # El comando recibido corresponde con los comandos de la funcion actual (func) ?
            match = (current_command == command_name_list[0]) or (current_command == command_name_list[1])

            if not match:
                # Si el comando enviado no concuerda con el recibido, buscamos otra funcion (shizu.py)
                return False

            # obtengo el mensaje virgen sin comandos
            message.content = message.content.replace(current_command, '').strip()

            # Si matcheo y t0do va bien procedo a ejecutar la funcion del comando
            await func(self, message, *args)

        return wrapper
    return decor


def avoid_external_calls(func):

    async def async_wrapper(*args):
        # Obtengo el nombre del archivo del metodo que esta llamando
        caller_frame = inspect.stack()[1]
        caller_filename = caller_frame.filename
        caller_filename = os.path.splitext(os.path.basename(caller_filename))[0]

        # Obtengo el nombre del archivo del metodo que se llama
        called_filename = func.__module__

        if called_filename == caller_filename:
            if inspect.iscoroutinefunction(func):
                return await func(*args)
            else:
                return func(*args)
        else:
            print("Ignorando llamada externa")
            return False

    def wrapper(*args):
        # Obtengo el nombre del archivo del metodo que esta llamando
        caller_frame = inspect.stack()[1]
        caller_filename = caller_frame.filename
        caller_filename = os.path.splitext(os.path.basename(caller_filename))[0]

        # Obtengo el nombre del archivo del metodo que se llama
        called_filename = func.__module__

        if called_filename == caller_filename:
            return func(*args)
        else:
            print("Ignorando llamada externa")
            return False

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return wrapper
