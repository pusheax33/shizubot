from datetime import datetime
from shizu_database import ShizuDatabase


class ShizuDocument:
    """
        Toda la creacion de documentos para las base de datos se hara en esta clase.
        Creacion de documento de guild, de usuario, para updatear experiencia, etc.
    """

    def __init__(self):
        self.shizu_database = ShizuDatabase()

    def create_task_document(self, task_name, task_type, message, minutes_until_execute=None, loop_times=None):
        # Verifica si un documento existe, si existe agrega la tarea al documento y devuelve el documento listo para agregar a la db
        # si no existe lo crea.
        # task_types: 
        #           time_task (task que se ejecuta cada cierto tiempo)
        #           realtime_task (task que se ejecuta al recibir una notificacion)
        
        if task_type == "time_task" and minutes_until_execute == None or loop_times == None:
            print("ERROR: la task es tipo time_task pero minutes_until_execute y/o loop_times no esta definido!")
            return None

        command_name = message.content
        # Verifico si el contenedor esta creado previamente asi no sobreescribo perdiendo las task_list
        task_container_doc = {
            "_id" : task_name,
            "name" : task_name,
            "command" : command_name,
            "task_type" : task_type,
            "created_time": datetime.now(),
            "tasks_list" : []
        }
        container_doc = self.shizu_database.get_document("tasks", {"_id": task_container_doc["_id"]})
        doc_exists = container_doc is not None

        if doc_exists:
            # Si existe el documento utilizo el container_doc existente ya que puede tener otros task en el task_list
            task_container_doc = container_doc
            # Verifico que en el task_list no haya previamente una task en el mismo canal, para evitar duplicaciones
            for inner_task in container_doc["tasks_list"]:
                if inner_task["channel_id"] == message.channel.id:
                    # Si es el mismo canal, entonces la tarea esta duplicada, la elimino
                    del container_doc["tasks_list"][container_doc["tasks_list"].index(inner_task)]

        # Finalmente agrego la nueva task al task_list
        task_doc = {
            "creator_id" : message.author.id,
            "message_id" : message.id,
            "channel_id" : message.channel.id,
            "created_time" : datetime.now(),
            "minutes_until_execute" : minutes_until_execute, # Tiempo en minutos en que la tarea va a ejecutarse
            "loop_times" : loop_times # 0 = infinitas veces
        }
        task_container_doc["tasks_list"].append(task_doc)

        return task_container_doc

    def create_guild_document(self, guild):
        # Crea documento de guild, esta funcion no verifica si la guild existe o no existe, se limita a crear el documento.
        channels = []
        for channel in guild.channels:
            channels.append({"id" : channel.id, "last_50_messages" : [], "tasks" : []})

        guild_doc = {
            "_id" : guild.id,
            "name" : guild.name,
            "owner_id" : guild.owner_id,
            "language" : "en",
            "channels" : channels # { "id" : 4546, tasks : []}
        }

        return guild_doc

    def create_user_document(self, discord_member):
        # guardo al usuario de discord en la coleccion de usuarios y retorno el id de la db del usuario
        # En la coleccion solo habran datos del usuario que no cambiaran, por ejemplo el nick no esta ya que el usuario puede cambiarlo
        # y requeriria updatear la db al detectar el cambio. Mas eficaz y facil obtener el usuario directamente de la api de discord.

        member_collection = {
            "_id": discord_member.id,
            "name": discord_member.name,
            "bot": discord_member.bot,
            "mention": discord_member.mention,
            "experience": 0,
            "level": 0,
            "shizy": 300,
            "message_count": 0,
            "last_message_time" : None
        }

        return member_collection

    def merge_documents(self, document1, document2):
        # Funcion recursiva
        # Funcion encargada de meter en el documento uno los cambios que hayan del documento 2.
        # documento1 va a ser sobreescrito por documento2 para datos directos, es decir
        # si documento1 tiene un campo -> "numero": 20 y documento2 tiene el campo "numero" : 30
        # se colocara en documento1 el campo del documento2, es decir "numero" : 30
        for key in document1:
            if type(document1[key]) == dict:
                document1[key] = self.merge_documents(document1[key], document2[key])
            elif type(document1[key] == list):
                # si el dato es lista, la lopeo y por cada documento dentro de la lista, hago recursion
                temp_list = []
                if len(document1[key] >= len(document2[key])):
                    for i in range(0, len(document1[key])):
                        upd_data = self.merge_documents(document1[key][i], document2[key][i])
                else:
                    for i in range(0, len(document2[key])):
                        upd_data = self.merge_documents(document1[key][i], document2[key][i])
            else:
                document1[key] = document2[key]
        return document1

