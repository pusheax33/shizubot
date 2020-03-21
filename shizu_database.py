from pymongo import MongoClient
import pprint
from core import debug_log
from datetime import datetime

class ShizuDatabase():

    database = None
    lvl_table = [100.0, 275.0, 800.0, 1825.0, 3500.0, 5975.0, 9400.0, 13925.0, 19700.0, 26875.0, 35600.0, 46025.0, 58300.0, 72575.0, 89000.0, 107725.0, 128900.0, 152675.0, 179200.0, 208625.0, 241100.0, 276775.0, 315800.0, 358325.0, 404500.0, 454475.0, 508400.0, 566425.0, 628700.0, 695375.0, 766600.0, 842525.0, 923300.0, 1009075.0, 1100000.0, 1196225.0, 1297900.0, 1405175.0, 1518200.0, 1637125.0, 1762100.0, 1893275.0, 2030800.0, 2174825.0, 2325500.0, 2482975.0, 2647400.0, 2818925.0, 2997700.0, 3183875.0, 3377600.0, 3579025.0, 3788300.0, 4005575.0, 4231000.0, 4464725.0, 4706900.0, 4957675.0, 5217200.0, 5485625.0, 5763100.0, 6049775.0, 6345800.0, 6651325.0, 6966500.0, 7291475.0, 7626400.0, 7971425.0, 8326700.0, 8692375.0, 9068600.0, 9455525.0, 9853300.0, 10262075.0, 10682000.0, 11113225.0, 11555900.0, 12010175.0, 12476200.0, 12954125.0, 13444100.0, 13946275.0, 14460800.0, 14987825.0, 15527500.0, 16079975.0, 16645400.0, 17223925.0, 17815700.0, 18420875.0, 19039600.0, 19672025.0, 20318300.0, 20978575.0, 21653000.0, 22341725.0, 23044900.0, 23762675.0, 24495200.0, 25242625.0, 26005100.0]

    def __init__(self, db = None):
        if not db:
            # creo/obtengo la database por defecto del bot, que sera 'shizu'
            self.database = self.get_connection().shizu


    @staticmethod
    def get_connection():
        return MongoClient()


    def add_field(self, spec, collection, document):
        """
            Agrega un campo no existente a un documento ya existente
            spec = diccionario con el documento a buscar, ejemplo {"_id" : 12132}
            collection = collection en donde se agregara el campo, ejemplo "members"
            document = diccionario a agregar, ejemplo {"likes" : 0}
        """
        self.database[collection].update_one(spec, {"$set" : document})
        debug_log(f"Agregando el documento {document} en la coleccion {collection}", "db")


    def save_guild(self, guild, guild_to_update=None):
        # Obtengo db de las guilds
        guilds = self.database.guilds
        db_guild = guilds.find({"_id" : guild.id})
        guild_doc_id = None

        channels = []
        for channel in guild.channels:
            channels.append({"id" : channel.id, "last_50_messages" : [], "tasks" : []})

        if db_guild.count() <= 0:
            print("guild no existe, procediendo a crear una nueva coleccion!")
            guild_dic = {
                "_id" : guild.id,
                "name" : guild.name,
                "owner_id" : guild.owner_id,
                "language" : "en",
                "channels" : channels # { "id" : 4546, tasks : []}
            }
            guild_doc_id = guilds.insert_one(guild_dic)

        if guild_to_update:
            db_guild = db_guild[0]
            debug_log("Guild ya existe, actualizando coleccion...", "db")
            guild_dic = {
                "_id" : db_guild["_id"],
                "name" : db_guild["name"],
                "owner_id" : db_guild["owner_id"],
                "language" : db_guild["language"],
                "channels" : db_guild["channels"] # { "id" : 4546, tasks : []}
            }
            for key in guild_to_update:
                # Inserto los datos a actualizar en los datos que ya habian previamente
                if key == "channels":
                    for channel in guild_to_update[key]:
                        for db_channel in guild_dic[key]:
                            if channel["id"] == db_channel["id"]:
                                db_channel = channel
                guild_dic[key] = guild_to_update[key]
                guild_doc_id = guilds.update({"_id" : guild.id}, guild_dic)
            
        if not guild_doc_id:
            debug_log(f"La funcion save_guild fue invocada para la guild {guild.name} con id {guild.id} pero ningun dato fue actualizado ni agregado.", "db")
        else:
            debug_log(f"La guild {guild.name} fue agregada correctamente a la DB")
        return guild_doc_id


    def save_task(self, message, minutes_until_execute, loop_times):
        # Guarda en la base de datos una tarea que se ejecutara a los minutos indicados por parametro.
        tasks = self.database.tasks
        guilds = self.database.guilds

        task_dic = {
            "creator_id" : message.author.id,
            "message_id" : message.id,
            "channel_id" : message.channel.id,
            "command" : message.content,
            "created_time" : datetime.now(),
            "minutes_until_execute" : minutes_until_execute, # Tiempo en minutos en que la tarea va a ejecutarse
            "loop_times" : loop_times # 0 = infinitas veces
        }

        # Agrego la task a la base de datos de las tasks
        task_id = tasks.insert_one(task_dic).inserted_id

        # Agrego el id de la task a la base de datos de la guild en que se creo la task
        db_guild = guilds.find({"_id" : message.guild.id})
        channel_id = message.channel.id
        if (db_guild.count() > 0): # Me aseguro que exista la guild, en teoria siempre deberia existir
            db_channels = db_guild[0]["channels"]
            for channel in db_channels:
                if channel["id"] == channel_id:
                    if "tasks" in channel:
                        channel["tasks"].append({"id": task_id})
                    else:
                        channel["tasks"] = [{"id": task_id}]

            guilds.update_one({"_id" : message.guild.id}, {"$set" : {"channel" : db_channels}})
            debug_log("Task agregada a la base de datos de la guild exitosamente.", "db")
        else:
            print("ERROR: Hubo un problema al guardar la task creada en la base de datos de la guild en la que se invoco al comando.")
            return

        return task_id

    def update_task(self, update_task_dic):
        tasks = self.database.tasks
        task_modified = False
        if update_task_dic:
            task_modified = tasks.update_one({"_id" : update_task_dic["_id"]}, {"$set": update_task_dic}).modified_count > 0
            debug_log("Actualizando los datos de una tarea existente", "db")
        else:
            print("Error: El diccionario recibido es None.")

        return task_modified

    def save_user(self, member, collection_to_update=None):
        # guardo al usuario de discord en la coleccion de usuarios y retorno el id de la db del usuario
        # En la coleccion solo habran datos del usuario que no cambiaran, por ejemplo el nick no esta ya que el usuario puede cambiarlo
        # y requeriria updatear la db al detectar el cambio. Mas eficaz y facil obtener el usuario directamente de la api de discord.

        members = self.database.members # obtengo la db de los miembros
        current_member = members.find({"_id" : member.id})
        member_id = None

        if current_member.count() <= 0:
            debug_log("Usuario no existe, procediendo a crear uno nuevo con datos pre establecidos.", "db")
            # No existe el id, procedo a crear nuevo usuario:
            member_collection = {
                "_id": member.id,
                "name": member.name,
                "bot": member.bot,
                "mention": member.mention,
                "experience": 0,
                "level": 0,
                "shizy": 300,
                "message_count": 0,
                "last_message_time" : None
            }
            member_id = members.insert_one(member_collection)

        # Llegados aca el user existe, procedo a actualizarlo con los datos que vienen por parametro
        if collection_to_update:
            # Como mongodb no actualiza los valores automaticamente tengo que yo hacerlos manual
            # Si no hago esto, la coleccion se va a borrar y colocar solamente los valores que esten en collection_to_update
            current_member = current_member[0]
            member_collection = {
                "_id": current_member["_id"],
                "name": current_member["name"],
                "bot": current_member["bot"],
                "mention": current_member["mention"],
                "experience": current_member["experience"], # Inician en nivel 0
                "level": current_member["level"],
                "shizy": current_member["shizy"], # Inician con 300 Shizys (Shizu cash)
                "message_count": current_member["message_count"],
                "last_message_time": datetime.now()
            }
            for key in collection_to_update:
                member_collection[key] = collection_to_update[key]

            member_id = members.update({"_id" : member.id}, member_collection)
        
        if not member_id:
            debug_log(f"La funcion save_user fue llamada para el miembro {member.name} pero ningun dato fue actualizado ni agregado.", "db")

        return member_id


    def remove(self, collection_name, dic):
        return self.database[collection_name].delete_one(dic)


    def add_experience(self, member, exp_to_add):
        # Retorna True si subio de nivel
        # Este metodo no tiene que estar aca
        # Metodo que agrega experiencia al usuario y sube de nivel en caso de que cumpla con las condiciones para subir.
        lvlup = False
        db_member = self.database.members.find({"_id" : member.id})[0]
        new_exp = db_member["experience"] + exp_to_add
        debug_log(f"Agregando {exp_to_add} de experiencia", "db")
        current_lvl = db_member["level"]

        if new_exp >= self.get_lvl_experience(current_lvl):
            current_lvl += 1 # Subo de nivel!
            lvlup = True

        update_coll = {
            'experience' : new_exp,
            'level' : current_lvl,
            'message_count' : db_member["message_count"] + 1
        }
        self.save_user(member, update_coll)

        return lvlup


    def get_lvl_experience(self, lvl):
        level_formula = 100 + ( 0.5*(lvl**3) + 2*(lvl**2) + lvl) * 50
        return level_formula


    def query(self, collection_name, doc, data_to_search=None):
        # Agregar error por si no existe la coleccion.
        query = self.database[collection_name].find(doc)
        if query.count() > 0:
            if data_to_search:
                query = query[0][data_to_search] # Creo que esta mal porque [0] me devuelve la posicion del primer cursor?
            else: 
                query = query[0]
        else:
            query = None

        return query


    def get_collection(self, collection_name):
        col = self.database[collection_name].find()
        if col.count() > 0:
            return col
        else :
            debug_log(f"Se intenta obtener la coleccion con nombre {collection_name} pero esta no existe en la db.")