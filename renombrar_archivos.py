import os

for dir in os.scandir('guilds/'):
    dirpath = 'guilds/' + dir.name
    for file in os.scandir(dirpath):
        filepath = dirpath + "/" + file.name
        if os.path.isfile(filepath):
            # No siempre funciona esto de abajo pero para el problema actual me sirve...
            extension = file.name.split(".")
            n_extension = [extension[0]]
            for x in extension[1:]:
                 n_extension.append("." + x) # le agrego el puntito que split elimina para evitar un bug mayor al usar join con imagenes que tengan multiple extensiones (no tiene sentido que haya una imagen asi pero quien sabe?)
            if len(n_extension[-1]) > 1:
                if n_extension[-1][1] == "j": # [0] es el punto y [1] la primer leetra
                    fixed_file_extension = "".join(n_extension[:-1]) + ".jpg"
                elif n_extension[-1][1] == "p": # [0] es el punto y [1] la primer leetra
                    fixed_file_extension = "".join(n_extension[:-1]) + ".png"
                elif n_extension[-1][1] == "g": # [0] es el punto y [1] la primer leetra
                    fixed_file_extension = "".join(n_extension[:-1]) + ".gif"
                else:
                    continue


            os.rename(filepath, dirpath + "/" + fixed_file_extension)