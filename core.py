from bot_vars import DEBUG, DEBUG_MESSAGE_FILTER
from datetime import datetime
import os
from discord import Message

def debug_log(text, message_type=None):
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

