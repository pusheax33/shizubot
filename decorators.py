from functools import wraps
import bot_vars
import asyncio


def commands(prefix=None, additional_prefix=None):
    def decor(func):
        func_name = func.__name__
        print("Fun NAME: " + func_name)
        command_prefix = bot_vars.COMMAND_PREFIX  # prefix del bot. Por defecto -> ;
        command_name_list = [command_prefix + (prefix or func_name), command_prefix + (additional_prefix or func_name)]

        @wraps(func)
        async def wrapper(self, message):
            """
                Haciendo test esta es la forma mas rapida de matchear que encontre. re.compile/match y
                startswith demoran mucho mas que esto.
            """
            if (message.content == "None"):
                await func(self, message)

            current_command = message.content.split(maxsplit=1)[0]

            # El comando recibido corresponde con los comandos de la funcion actual (func) ?
            match = (current_command == command_name_list[0]) or (current_command == command_name_list[1])

            if not match:
                # Si el comando enviado no concuerda con el recibido, buscamos otra funcion (shizu.py)
                return False

            # obtengo el mensaje virgen sin comandos
            message.content = message.content.replace(current_command, '').strip()

            # Si matcheo y t0do va bien procedo a ejecutar la funcion del comando
            await func(self, message)

        return wrapper
    return decor

def decotest(metodo):
    def decor2(func):
        print("deccorrr!")
    
        @wraps(func)
        async def wrapper2(self, message):
            print("wrapper!!")
            await metodo(self, message)
            await func(self, message)
        return wrapper2
    return decor2