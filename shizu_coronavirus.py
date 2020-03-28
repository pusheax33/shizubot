import requests
from decorators import *
import re
from shizu_database import ShizuDatabase
from shizu_tasks import ShizuTasks
from datetime import datetime
from shizu_document import ShizuDocument
import traceback

class CoronaVirusData:
    # Clase creada solo para los metodos estaticos. En realidad deberia re hacer el decorators para evitar esto que no es lo ideal.
    previous_datalist = {}



    def cvidupdate(self):
        resp = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vQuDj0R6K85sdtI8I-Tc7RCx8CnIxKUQue0TCUdrFOKDw9G3JRtGhl64laDd3apApEvIJTdPFJ9fEUL/pubhtml?gid=0&single=true")
        #print(resp.text)
        regx_country = r'class=\"s0\">\d{0,10}((?:</td><td class=\"s0\">)|(?:</td><td class=\"s0 softmerge\"><div class=\"softmerge-inner\" style=\"width: 97px; left: -1px;\">))(.*?)(?:(?:</div>)|(?:</td><td class=\"s1\"))'
        regx_data = r'class=\"s1\">([\d]*)</td>'
        matches = re.finditer(regx_data, resp.text, re.MULTILINE)
        matches_country = re.finditer(regx_country, resp.text, re.MULTILINE)
        actual_datalist = {}

        country_list = []

        
        # Obtengo paises
        for matchNum2, match in enumerate(matches_country, start=1):
            country_list.append(match.group(2))

        data_temp_list = []
        counter = 0
        # Obtengo data
        for matchNum, match in enumerate(matches, start=1):
            data_temp_list.append(match.group(1))
            if len(data_temp_list) == 3:
                # actual_datalist["pais"] = [bla, bla, bla]
                actual_datalist[country_list[counter]] = data_temp_list
                data_temp_list = []
                counter +=1


        # Listo, en data_list esta toda la data de los casos, muertes y recuperados con el sig formato:
        # [ [pais1, casos, muertes, recuperaciones], [pais2, casos, muertes, recuperados], etc ]...
        #print(datalist)

        if len(self.previous_datalist) == 0:
            # Si recien enciendo el bot la previous datalist va a estar vacia, no necesito hacer lo de abajo porque fallara.
            self.previous_datalist = actual_datalist
            return

        discord_response = ""
        for country_name in actual_datalist:
            if len(actual_datalist) != len(self.previous_datalist):
                discord_response = "El data set anterior es distinto al dataset actual :o, no se pudo comparar paises. Data set anterior actualizado al actual."
                print(len(actual_datalist), actual_datalist)
                print(len(self.previous_datalist), self.previous_datalist)
                break
            
            try:
                actual_cases = int(actual_datalist[country_name][0])
                actual_deaths = int(actual_datalist[country_name][1])
                actual_recoveries = int(actual_datalist[country_name][2])

                # ME ASEGURO que el pais exista en previous datalist asi evito explosiones!
                try:
                    self.previous_datalist[country_name]
                except KeyError:
                    self.previous_datalist[country_name] = [0, 0, 0]

                previous_cases = int(self.previous_datalist[country_name][0])
                previous_deaths = int(self.previous_datalist[country_name][1])
                previous_recoveries = int(self.previous_datalist[country_name][2])
            except Exception:
                discord_response = "Sucedio una excepcion al intentar obtener la data de paises, casos, muertes y recuperados. No puedo continuar D:"
                print(len(actual_datalist), actual_datalist)
                print(len(self.previous_datalist), self.previous_datalist)
                traceback.print_exc()
                break

            # No utilizo math.abs porque puede haber situaciones donde se agregue uno o mas casos nuevo al dataset
            # Y posteriormente se elimine ese caso nuevo debido a que fue un error
            # dando como resultado un caso negativo, al obtener caso negativo puedo saber si hubo un error
            # Si uso abs dara siempre positivo y figurara nuevos casos siempre.
            cases_result = actual_cases - previous_cases
            deaths_result = actual_deaths - previous_deaths
            recoveries_result = actual_recoveries - previous_recoveries

            partial_response = ""
            if cases_result > 0:
                partial_response += f"[+{cases_result} casos] "
            if deaths_result > 0:
                partial_response += f"[+{deaths_result} muertes] "
            if recoveries_result > 0:
                partial_response += f"[+{recoveries_result} recuperados]"

            if partial_response != "":
                # Significa que hay data nueva para actualizar, entonces agrego el pais
                discord_response += "**"+country_name.upper() + f"** ---> {partial_response}. Total -> {actual_cases} casos, {actual_deaths} muertes, {actual_recoveries} recuperados.\n\n"

        for key in actual_datalist:
            self.previous_datalist[key] = actual_datalist[key]
        print("RESPONSE: " + discord_response)
        return discord_response

    def get_country_data(self, country_name):
        try:
            data = self.previous_datalist[country_name]
            return "**"+country_name + f"** casos totales -> {data[0]} casos, {data[1]} muertes, {data[2]} recuperados.\n\n"
        except KeyError:
            return f"No se encontro el pais {country_name}. Los nombres de paises deben estar en ingles."
        

class ShizuCoronaVirus():

    def __init__(self, shizu):
        self.coronavirusdata = CoronaVirusData()
        self.shizu_document = ShizuDocument()
        self.shizu = shizu


    @commands("cvid")
    async def coronavirus(self, message):
        if not message.content:
            return await message.channel.send("Para activar el comando ingresa ;cvid enable o ;cvid disable para desactivar.")
            
        data_check_update_time = 1 # cada cuanto tiempo verificara si hay datos nuevos.
        func_to_call_name = ";cvidcheckupd"
        minutes_until_execute = 1
        command = message.content[0]

        if message.content == "":
            return await message.channel.send("Para activar las notificaciones ingresa ;cvid enable. Para desactivar ;cvid disable")

        # Esta task esta compuesta por tasks : [{ name: "coronavirus", "command": ";cvidcheckupd", task_list = [task1, task2, task3]},...]
        # task1, task2, task3 se crean cuando se llama al comando en un server/canal distinto
        # cada una de esas task debe ejecutarse cada minuto en un loop, es decir, shizu debe enviar el mensaje de infectados
        # a cada uno de esos servers que figuran en las task.

        message.content = func_to_call_name
        doc = self.shizu.shizu_document.create_task_document("coronavirus", "realtime_task", message, data_check_update_time, 0)

        # entro en la coleccion "tasks" de la db y verifico si doc ya esta
        db_task = self.shizu.database.get_document("tasks", doc["_id"])
        task_container_exists = db_task != None

        if command == "e": 
            # Activo las notificaciones de coronavirus
            if task_container_exists:
                # verifico si esta la task en el interior
                task_list = db_task["tasks_list"]
                for inner_task in task_list:
                    if inner_task["channel_id"] == message.channel.id:
                        return await message.channel.send("Etto... las notificaciones ya estaban activadas, amigite!!")
            
            # Creo la task en la base de datos, se ejecutara cada 1 minuto.
            new_task_id = self.shizu.database.save_task(doc)
            if not new_task_id:
                return await message.channel.send("Hubo un error inesperado al crear la task en la base de datos :/") 
                
            # empiezo la task que cree arriba
            self.shizu.shizu_tasks.start_task(doc)
            await message.channel.send("Ok perro, notificaré cuando encuentre datos nuevos!!\nEscribe ;cvid disable para deshabilitar el comando!")
            # Una vez activado el comando ejecuto inmediatamente para que setee en la lista previa de datos los datos actuales, asi
            # al minuto pueda comenzar a calcular datos
            return await self.cvidcheckupd(message)

        if command == "d":
            founded = False
            task_list = db_task["tasks_list"]
            for inner_task in task_list:
                if inner_task["channel_id"] == message.channel.id:
                    founded = True
            if not founded:
                return await message.channel.send("Error, estas intentando deshabilitar algo que NO existe en la DB!")


            # Procedo a quitar la task de la base de datos...
            # Por logica la task actual es la ultima en la lista de task ya que arriba fue agregada al container
            # al ejecutar create_task_document
            del doc["tasks_list"][-1]
            if len(doc["tasks_list"]) == 0:
                # Elimino el taskcontainer de la DB y de la lista de tasks
                result = self.shizu.database.remove_document("tasks", {"_id" : db_task["_id"]})
                task_result = await self.shizu.shizu_tasks.remove_task(db_task["_id"])
            else:
                # Actualizo el task container en la DB y en la lista de TASKS reflejando la task eliminada actual.
                result = self.shizu.database.update_task(doc)
                task_result = await self.shizu.shizu_tasks.update_task(db_task["_id"], doc)
            print("RESULT: ", result)
            print("task_del: ", task_result)
            if not result or not task_result:
                return await message.channel.send("Yabai! La tarea no pudo ser eliminada de la base de datos, no pudo ser eliminada de las tareas que se estan ejecutando actualmente o ambas!")
            else:
                return await message.channel.send("Ok perro, no te notificaré mas sobre esto.")

        return await message.channel.send("Hubo un error desconocido!")


    @commands("cvidcases")
    async def cases(self, message):
        country = message.content.upper()
        resp = self.coronavirusdata.get_country_data(country)
        try:
            #await message.delete(delay=5)
            pass
        except Exception:
            pass
        await message.channel.send(resp)
        
    
    @commands()
    async def cvidcheckupd(self, message):
        """
            Este comando no es ideado para ser utilizado en el chat de discord.
            Este comando es utilizado por ;coronavirus, especificamente se llama cuando es momento
            de chequear actualizaciones por el coronavirus
            A este comando lo llama la base de datos.
        """
        cvid_doc = self.shizu.database.get_document("tasks", {"_id" : "coronavirus"})
        if cvid_doc != None:
            response = self.coronavirusdata.cvidupdate()
            if response:
                for task in cvid_doc["tasks_list"]:
                    message = await self.shizu.get_message(task["channel_id"], task["message_id"])
                    # actualizo el tiempo de las task interiores.. nose para que, en realtime_task no es necesario.. pero bueno
                    task["created_time"] = datetime.now() 
                    await message.channel.send(response)


    @commands()
    async def cvidinfo(self, message):
        if len(self.coronavirusdata.previous_datalist) == 0:
            await message.channel.send("Debe pasar un minuto hasta que tenga datos.")

        global_data = self.coronavirusdata.previous_datalist
        cases = 0
        recoveries = 0
        deaths = 0
        for country_data in global_data:
            cases += int(country_data[1])
            recoveries += int(country_data[2])
            deaths += int(country_data[3])
        
        discord_message = f"Datos globales: Infectados: {cases}, muertes: {recoveries}, recuperados: {deaths}."
        await message.channel.send(discord_message)





CoronaVirusData().cvidupdate()