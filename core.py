from bot_vars import DEBUG, DEBUG_MESSAGE_FILTER
from datetime import datetime
import os
from discord import Message

def debug_log(text, message_type=None):
    # Cada mensaje enviado a debug_log se le puede agregar un parametro extra que es el tipo de mensaje
    # Por ejemplo si uso debug_log para un mensaje de database le agrego de message_type "db"
    # Esta funcion verifica si:
    #   a) Esta activado el debug?
    #   b) En bot_vars.DEBUG_MESSAGE_FILTER esta seleccionado que se muestren todos los mensajes (All) o solamente el de un tipo en especifico?
    #   c) Si esta seleccionado un tipo en especifico, por ejemplo "db" y el message_type de esta funcion tambien es "db", entonces muestra el mensaje
    # TODO: Agregar multiples tipos de mensajes
    if DEBUG and (DEBUG_MESSAGE_FILTER == "ALL" or DEBUG_MESSAGE_FILTER == message_type):
        now = datetime.now()
        time = "[%d:%d:%d] " % (now.hour, now.minute, now.second)
        print(time + str(text))

def GetSavedEmojis():
    if not os.path.exists('guilds/'):
        print("No puedo obtener los emojis porque no existe la carpeta guild/")
        return

    emojis_path_list = []
    for dir in os.scandir('guilds/'):
        dirpath = 'guilds/' + dir.name
        for file in os.scandir(dirpath):
            filepath = dirpath + "/" + file.name
            if os.path.isfile(filepath):
                emojis_path_list.append(filepath)
            else:
                print("no hay archivos en este server")
    return emojis_path_list


def get_saved_images():
    if not os.path.exists('images/guilds/'):
        return print("No puedo obtener las imagenes porque no existe la carpeta images/guilds/")

    images_path_list = []
    for dir in os.scandir('images/guilds/'):
        dirpath = 'images/guilds/' + dir.name
        for file in os.scandir(dirpath):
            filepath = dirpath + "/" + file.name
            if os.path.isfile(filepath):
                images_path_list.append(filepath)
            else:
                print("no hay archivos en este server")
    return images_path_list

