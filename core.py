from bot_vars import DEBUG
from datetime import datetime
import os

def debug_log(text):
    now = datetime.now()
    time = "[%d:%d:%d] " % (now.hour, now.minute, now.second)
    if DEBUG:
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

    
