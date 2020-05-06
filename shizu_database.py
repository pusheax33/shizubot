from pymongo import MongoClient
import pprint
from core import debug_log
from datetime import datetime
import traceback

class ShizuDatabase():
    """ 
        La base de datos en mongodb esta formada por colecciones y documentos
        Una coleccion posee uno o varios documentos dentros, por ejemplo coleccion guilds tendra todas las guilds en las que el bot esta, ej:
            collection_guild : {guild_doc1, guild_doc2, ...}
        Un documento es un json/dictionary donde se guarda todos los datos.
    """

    database = None
    lvl_table = [100.0, 275.0, 800.0, 1825.0, 3500.0, 5975.0, 9400.0, 13925.0, 19700.0, 26875.0, 35600.0, 46025.0, 58300.0, 72575.0, 89000.0, 107725.0, 128900.0, 152675.0, 179200.0, 208625.0, 241100.0, 276775.0, 315800.0, 358325.0, 404500.0, 454475.0, 508400.0, 566425.0, 628700.0, 695375.0, 766600.0, 842525.0, 923300.0, 1009075.0, 1100000.0, 1196225.0, 1297900.0, 1405175.0, 1518200.0, 1637125.0, 1762100.0, 1893275.0, 2030800.0, 2174825.0, 2325500.0, 2482975.0, 2647400.0, 2818925.0, 2997700.0, 3183875.0, 3377600.0, 3579025.0, 3788300.0, 4005575.0, 4231000.0, 4464725.0, 4706900.0, 4957675.0, 5217200.0, 5485625.0, 5763100.0, 6049775.0, 6345800.0, 6651325.0, 6966500.0, 7291475.0, 7626400.0, 7971425.0, 8326700.0, 8692375.0, 9068600.0, 9455525.0, 9853300.0, 10262075.0, 10682000.0, 11113225.0, 11555900.0, 12010175.0, 12476200.0, 12954125.0, 13444100.0, 13946275.0, 14460800.0, 14987825.0, 15527500.0, 16079975.0, 16645400.0, 17223925.0, 17815700.0, 18420875.0, 19039600.0, 19672025.0, 20318300.0, 20978575.0, 21653000.0, 22341725.0, 23044900.0, 23762675.0, 24495200.0, 25242625.0, 26005100.0]

    def __init__(self, db = None):
        if not db:
            # creo/obtengo la database por defecto del bot, que sera 'shizu'
            self.database = self.get_connection().shizu

    @staticmethod
    def get_connection():
        return MongoClient()

    def add_field(self, spec, collection_name, field_doc):
        """
            Agrega un campo no existente a un documento ya existente
            spec = diccionario con el documento a buscar, ejemplo {"_id" : 12132}
            collection = collection en donde se agregara el campo, ejemplo "members"
            document = diccionario a agregar, ejemplo {"likes" : 0}
        """
        self.database[collection_name].update_one(spec, {"$set" : field_doc})
        debug_log(f"Agregando el documento {field_doc} en la coleccion {collection_name}", "db")

    def update_field(self, spec, collection_name, field_doc):
        # Verificar si el documento y campo existe, si existe lo actualizo y retorno el id del doc, sino retorno None/False.
        pass

    def remove_field(self, spec, collection_name, field_doc):
        # Verificar si el documento y campo existe, si existe lo elimino y retorno True, sino retorno None/False.
        pass

    def add_document(self, collection_name, document):
        """
            Retorna el documento agregado a la DB.
            Esta clase no debe utilizarse para documentos que pueden ya existir en la DB porque no comprueba si existen
            para documentos que pueden existir se debe usar update_or_add_document()
        """
        try:
            return self.database[collection_name].insert_one(document).inserted_id # retorna id si lo guarda, none si no.
        except Exception:
            traceback.print_exc()
         
    def update_document(self, collection_name, document):
        """
            Retorna True si la actualizacion del documento fue exitosa.
            Retorna False si hubo un error al actualizar el documento.
        """
        try:
            doc_modified = self.database[collection_name].update_one({"_id" : document["_id"]}, {"$set": document})
            return doc_modified.modified_count > 0
        except Exception:
            traceback.print_exc()

    def remove_document(self, collection_name, document):
        # Verificar si existe el doc, si existe lo elimino y retorno True, sino retorno false.
        if self.document_exists(collection_name, document):
            try:
                return self.database[collection_name].delete_one(document).deleted_count > 0
            except Exception:
                traceback.print_exc()
        return False

    def update_or_add_document(self, collection_name, document):
        # Verifico si el documento existe, si existe lo actualizo llamando a update_document, sino lo creo llamando add_document
        if self.document_exists(collection_name, document):
            return self.update_document(collection_name, document)

        return self.add_document(collection_name, document)

    def get_documents(self, collection_name):
        # Devuelve todos los documentos contenidos en una collecciono
        return self.database[collection_name].find()

    def get_document(self, collection_name, doc):
        # Devuelve el primer documento encontrado
        doc = self.database[collection_name].find_one(doc)
        return doc

    def document_exists(self, collection_name, document):
        return self.get_document(collection_name, {"_id": document["_id"]}) != None

    def save_task(self, task_doc):
        """
            Si la task existe reemplaza la task en la base de datos con el parametro task_doc
            Si no existe, crea el documento en la base de datos
        """
        task_id = self.update_or_add_document("tasks", task_doc)

        return task_id

    def update_task(self, update_task_doc):
        if update_task_doc:
            task_modified = self.update_document("tasks", update_task_doc)
            debug_log("Actualizando los datos de una tarea existente", "db")
        else:
            debug_log("Error: El diccionario recibido es None.")

        return task_modified

    def save_guild(self, guild_doc):
        # Agrega la guild solo si no existe en DB
        if not self.document_exists("guilds", guild_doc):
            guild_doc_id = self.add_document("guilds", guild_doc)
            debug_log("La guild {0} fue guardada en la DB.".format(guild_doc["name"]))
            return guild_doc_id

        debug_log("La guild {0} ya existe en la DB, ignorando!...".format(guild_doc["name"]))
        return None

    def save_member(self, member_doc):
        """
            Guarda el usuario UNICAMENTE si NO existe en la DB.
            Para actualizar utilizar update_document
        """
        if not self.document_exists("members", {"_id" : member_doc["_id"]}):
            # No existe, guardo nueveo user en db.
            current_member = self.add_document("members", member_doc)
            debug_log("El usuario {0} fue guardado en la DB.".format(member_doc["name"]))
            return current_member

        debug_log("El usuario {0} ya existe en la DB, ignorando!...".format(member_doc["name"]))
        return None

    def add_experience(self, member, exp_to_add):
        # Retorna True si subio de nivel
        # Este metodo no tiene que estar aca
        # Metodo que agrega experiencia al usuario y sube de nivel en caso de que cumpla con las condiciones para subir.
        lvlup = False
        db_member = self.get_document("members", {"_id" : member.id})
        new_exp = db_member["experience"] + exp_to_add
        debug_log(f"Agregando {exp_to_add} de experiencia", "db")
        current_lvl = db_member["level"]

        print("EXP PARA PROX LVL:", self.get_lvl_experience(current_lvl))
        if new_exp >= self.get_lvl_experience(current_lvl):
            current_lvl += 1 # Subo de nivel!
            lvlup = True

        db_member["experience"] = new_exp
        db_member["level"] = current_lvl
        db_member["message_count"] += 1 
        self.update_document("members", db_member)

        print("LEVEL UP??? ", lvlup)
        return lvlup

    def get_lvl_experience(self, lvl):
        level_formula = 100 + ( 0.5*(lvl**3) + 2*(lvl**2) + lvl) * 50
        return level_formula
