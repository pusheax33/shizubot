import requests
from decorators import *
import re
from shizu_database import ShizuDatabase
from shizu_tasks import ShizuTasks


# Decorador basico que hace ignorar que metodos se ejecuten mediante comandos de chat en discord
# En general esto hay que colocarlo dentro del .py de cada archivo que se desee ignorar metodos
# lo cual no es practico xq estaria la misma funcion en muchos .py.
# La solucion seria crear un decorador general que detecte el metodo de quien llama y el metodo a ejcutar
# y depende de eso ignore o no ignore la call. Pero hacerlo es mas complejo de lo que parece asique queda como TODO
def ignorecalls(func):
    if __name__ == "__main__":
        return func
    else:
        print("call ignorada")
        return False

class CoronaVirusData:
    # Clase creada solo para los metodos estaticos. En realidad deberia re hacer el decorators para evitar esto que no es lo ideal.
    previous_datalist = []

    def cvidupdate(self):
        resp = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vQuDj0R6K85sdtI8I-Tc7RCx8CnIxKUQue0TCUdrFOKDw9G3JRtGhl64laDd3apApEvIJTdPFJ9fEUL/pubhtml?gid=0&single=true")
        #print(resp.text)
        regx_country = r'class=\"s0\">\d{0,10}((?:</td><td class=\"s0\">)|(?:</td><td class=\"s0 softmerge\"><div class=\"softmerge-inner\" style=\"width: 97px; left: -1px;\">))(.*?)(?:(?:</div>)|(?:</td><td class=\"s1\"))'
        regx_data = r'class=\"s1\">([\d]*)</td>'
        matches = re.finditer(regx_data, resp.text, re.MULTILINE)
        matches_country = re.finditer(regx_country, resp.text, re.MULTILINE)
        datalist = []

        temp_list = []
        # Obtengo data
        for matchNum, match in enumerate(matches, start=1):
            
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                temp_list.append(match.group(groupNum))
                if len(temp_list) == 3:
                    datalist.append(temp_list)
                    temp_list = []

        # Obtengo paises
        for matchNum2, match in enumerate(matches_country, start=1):
            datalist[matchNum2-1].insert(0, match.group(2))

        # Listo, en data_list esta toda la data de los casos, muertes y recuperados con el sig formato:
        # [ [pais1, casos, muertes, recuperaciones], [pais2, casos, muertes, recuperados], etc ]...
        #print(datalist)

        if len(self.previous_datalist) == 0:
            # Si recien enciendo el bot la previous datalist va a estar vacia, no necesito hacer lo de abajo porque fallara.
            self.previous_datalist = datalist
            return

        discord_response = ""
        for country_index in range(0, len(datalist)):
            if len(datalist) != len(self.previous_datalist):
                discord_response = "El data set anterior es distinto al dataset actual :o, no se pudo comparar paises. Data set anterior actualizado al actual."
                print(len(datalist), datalist)
                print(len(self.previous_datalist), self.previous_datalist)
                break

            # ==================== DATA DE PAISES =====================
            try:
                actual_country = datalist[country_index][0]
                actual_cases = int(datalist[country_index][1])
                actual_deaths = int(datalist[country_index][2])
                actual_recoveries = int(datalist[country_index][3])

                previous_country = self.previous_datalist[country_index][0]
                previous_cases = int(self.previous_datalist[country_index][1])
                previous_deaths = int(self.previous_datalist[country_index][2])
                previous_recoveries = int(self.previous_datalist[country_index][3])
            except Exception:
                discord_response = "Sucedio una excepcion al intentar obtener la data de paises, casos, muertes y recuperados. No puedo continuar D:"
                print(len(datalist), datalist)
                print(len(self.previous_datalist), self.previous_datalist)
                break

            if actual_country != previous_country:
                discord_response = "El index del pais del dataset anterior difiere con el index del pais del dataset actual. Verificar que paso?"
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
                discord_response += actual_country.upper() + f" ---> {partial_response}. **Total** -> {actual_cases} casos, {actual_deaths} muertes, {actual_recoveries} recuperados. \n"

        self.previous_datalist = datalist
        print("RESPONSE: " + discord_response)
        return discord_response
                

class ShizuCoronaVirus:

    def __init__(self, shizu):
        self.database = ShizuDatabase()
        self.shizu = shizu
        self.shizu_tasks = ShizuTasks()
        self.coroanvirusdata = CoronaVirusData()

    @commands("cvid")
    async def coronavirus(self, message):
        data_check_update_time = 1 # cada cuanto tiempo verificara si hay datos nuevos.
        func_to_call_name = ";cvidcheckupd"
        if message.content == "":
            return await message.channel.send("Para activar las notificaciones ingresa ;cvid enable. Para desactivar ;cvid disable")

        # Verifico si ya existe la task
        doc = {
            "channel_id" : message.channel.id,
            "command" : func_to_call_name
        }
        # entro en la coleccion "tasks" de la db y verifico si doc ya esta
        db_task = self.database.query("tasks", doc)
        task_exists = db_task != None

        if message.content[0] == "e": 
            # Activo las notificaciones de coronavirus
            if task_exists:
                return await message.channel.send("Etto... las notificaciones ya estaban activadas, amigite!!")
            
            # La base de datos llamara al comando ;cvidcheckupd que se encargara de verificar si hay datos nuevos y responder en chat.
            message.content = ";cvidcheckupd"
            # Creo la task en la base de datos, se ejecutara cada 1 minuto.
            new_task_id = self.database.save_task(message, 1, 0)
            if not new_task_id:
                return await message.channel.send("Hubo un error inesperado al crear la task en la base de datos :/") 
                
            # creo la task para que comience a ejecutarse
            self.shizu_tasks.create_task(new_task_id, message.content, data_check_update_time, 0, self.cvidcheckupd, message)
            await message.channel.send("Ok perrito, notificaré cuando encuentre datos nuevos!!\nEscribe ;cvid disable para deshabilitar el comando!")
            # Una vez activado el comando ejecuto inmediatamente para que setee en la lista previa de datos los datos actuales, asi
            # al minuto pueda comenzar a calcular datos
            message.content = func_to_call_name
            return await self.cvidcheckupd(message)

        if message.content[0] == "d":
            if not task_exists:
                return await message.channel.send("Intentas deshabilitar algo QUE NO EXISTE EN LA DB, sos tonto?")

            # Procedo a quitar la task de la base de datos...
            result = self.database.remove("tasks", {"_id" : db_task["_id"]})
            print("RESULT: ",result)

            task_deleted = await self.shizu.shizu_tasks.remove_task(db_task["_id"])
            print("task_del: ", task_deleted)
            if not result or not task_deleted:
                return await message.channel.send("Yabai! La tarea no pudo ser eliminada de la base de datos, no pudo ser eliminada de las tareas que se estan ejecutando actualmente o ambas!")
            else:
                return await message.channel.send("Ok perrito, no te notificaré mas sobre esto.")

        return await message.channel.send("Hubo un error desconocido!")

    
    @commands()
    async def cvidcheckupd(self, message):
        """
            Este comando no es ideado para ser utilizado en el chat de discord.
            Este comando es utilizado por ;coronavirus, especificamente se llama cuando es momento
            de chequear actualizaciones por el coronavirus
            A este comando lo llama la base de datos.
        """
        response = self.coroanvirusdata.cvidupdate()
        if response:
            await message.channel.send(response)

    @commands()
    async def cvidinfo(self, message):
        self.cvidcheckupd(message)

        global_data = self.coroanvirusdata.previous_datalist
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