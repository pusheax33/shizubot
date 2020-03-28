import time
from datetime import datetime
import inspect
from threading import Timer
import bot_vars
from core import debug_log
from shizu_database import ShizuDatabase
from shizu_document import ShizuDocument

class ShizuTasks():

    tasks = []
    realtime_task = []

    def __init__(self, shizu):
        self.shizu = shizu
        self.shizu_database = ShizuDatabase()
        self.shizu_documents = ShizuDocument()
        print("Fui instanciada!!!!!!!!!!!!!!!!!! eeeeewawawawawaa!!!")

    def create_task(self, task_name, message, minutes_until_execute, loop_times):
        # el tiempo en que se creo la task debe re setearse cada vez que se ejecuta la task
        task_doc = self.shizu_documents.create_task_document(task_name, message, minutes_until_execute, loop_times)
        return task_doc

    async def remove_task(self, task_id):
        index = -1
        for task in self.tasks:
            if task["_id"] == task_id:
                index = self.tasks.index(task)
                break

        if index != -1:
            del self.tasks[index]
            return True
        return False

    async def update_task(self, task_id, task_doc):
        index = -1
        for task in self.tasks:
            if task["_id"] == task_id:
                index = self.tasks.index(task)
                break
        if index >= 0:
            del self.tasks[index]
            self.tasks.append(task_doc)
            return True
        return False

    def start_task(self, task):
        # Verifico si ya hay una task con mismo nombre, en caso de que haya la elimino para evitar task duplicadas
        # elimino la vieja y agrego la recibida por parametro

        for current_task in self.tasks:
            if current_task["name"] == task["name"]:
                del self.tasks[self.tasks.index(current_task)]

        self.tasks.append(task)

    async def check_tasks(self):
        # Verifica tasks de tipo time_task en base de datos que deben ser ejecutadas y la ejecuta
        # print(self.tasks)
        for task_container in self.tasks:
            if task_container["task_type"] == "realtime_task":
                # Las tareas en tiempo real no deberian siquiera estar en self.task, pero por las dudas.
                await self.check_realtime_task(task_container)

            if task_container["task_type"] == "time_task":
                await self.check_timetask(task_container)

    async def check_realtime_task(self, task_container):
        # las realtime_task por ahora todas se verificaran cada 1 minuto.
        actual_time = datetime.now()
        seconds_left = (task_container["created_time"] - actual_time).total_seconds() + (1 * 60) # segundos restante para la ejecucion

        if seconds_left <= 0: # Hora de ejecutar la tarea
            # Mando a ejecutar la tarea mediante shizu.py
            # al ser un realtime_task no necesito mandar el message, debo mandar solo el comando a ejecutar.

            for inner_task in task_container["tasks_list"]:
                # Obtengo un mensaje random para que call_commands funcione correctamente, super hacky y aun asi puede fallar esto.
                random_message = await self.shizu.get_message(inner_task["channel_id"], inner_task["message_id"])
                if random_message: break

            random_message.content = task_container["command"]
            await self.shizu.call_commands(random_message)

            # Actualizo el tiempo y actualizo la DB para reflejar el tiempo!
            task_container["created_time"] = actual_time
            self.shizu_database.update_document("tasks", task_container)


    async def check_timetask(self, task_container):
        """
            Ejemplo un task_container de tipo timetask:
            {
                {
                "_id" : ObjectId("5e7527850b49513351d2fca3"),
                "name" : "remindme",
                "command" : ";remindNotify",
                "task_type": "time_task",
                "task_list" : 
                {
                    "creator_id" : NumberLong("660270017601863720"),
                    "message_id" : NumberLong("690658144162152468"),
                    "channel_id" : NumberLong("690652611824582738"),
                    "created_time" : ISODate("2020-03-20T17:43:20.075Z"),
                    "minutes_until_execute" : 50,
                    "loop_times" : 1
                }, 
                {
                    ...
                }
            }
        """
        task_list = task_container["tasks_list"]

        for current_task in task_list:
            actual_time = datetime.now()
            seconds_left = (current_task["created_time"] - actual_time).total_seconds() + (current_task["minutes_until_execute"] * 60) # segundos restante para la ejecucion

            if seconds_left <= 0: # Hora de ejecutar la tarea
                message_id = current_task["message_id"]
                channel_id = current_task["channel_id"]

                # Mando a ejecutar la tarea mediante shizu.py
                message = await self.shizu.get_message(channel_id, message_id)
                message.content = task_container["command"]
                await self.shizu.call_commands(message)
                # Actualizo el tiempo!
                current_task["created_time"] = actual_time

                if current_task["loop_times"] > 0: 
                    current_task["loop_times"] -= 1 # Resto 1 a la cantidad de veces que se ejecuta la tarea

                    if current_task["loop_times"] == 0: # hora de eliminar la task actual
                        # Elimino la current_task del task_list, y si el task_list no tiene ninguna task
                        # elimino el task_container de self.task y de la base de datos.
                        if len(task_list) > 1: # len > 1 significa que hay otra tarea en task_list ademas de esta(current_task)
                            # Elimino la current_task de self.task y actualizo la DB reflejando el cambio
                            del task_list[task_list.index(current_task)]
                            updated = self.shizu_database.update_document("tasks", task_container)
                            if not updated:
                                print("Se intento actualizar una tarea de la base de datos pero los documentos actualizados son cero.")
                            continue
                        else:
                            # loop_times = 1, por lo que current_task es la ULTIMA tarea dentro de task_list, se procede a eliminar
                            # el task_container de self.task y de la DB
                            del self.tasks[self.tasks.index(task_container)]
                            self.shizu_database.remove_document("tasks", task_container)
                            continue

                # como la tarea debe seguir ejecutandose actualizo la db para reflejar
                # el cambio en loop_times y create_time.
                self.shizu_database.update_document("tasks", task_container)
