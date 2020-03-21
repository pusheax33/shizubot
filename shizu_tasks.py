import time
from datetime import datetime
import inspect
from threading import Timer
import bot_vars
from core import debug_log
from shizu_database import ShizuDatabase

class ShizuTasks():

    tasks = []

    def __init__(self):
        self.shizu_database = ShizuDatabase()
        print("Fui instanciada!!!!!!!!!!!!!!!!!! eeeeewawawawawaa!!!")

    def create_task(self, task_id, command, minutes_until_execute, loop_times, function, *args):
        # el tiempo en que se creo la task debe re setearse cada vez que se ejecuta la task
        task_dic = {
            "_id" : task_id,
            "minutes_until_execute" : minutes_until_execute,
            "loop_times" : loop_times,
            "created_time" : datetime.now(),
            "function" : [function, *args],
            "command" : command
            }
        self.tasks.append(task_dic)

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

    def start_task(self, task):
        self.tasks.append(task)


    async def check_tasks(self):
        # Verifica tasks en base de datos que deben ser ejecutadas y la ejecuta
        print(self.tasks)
        for task_dic in self.tasks:
            task_id = task_dic["_id"]
            minutes_until_execute = task_dic["minutes_until_execute"]
            loop_times = task_dic["loop_times"]
            created_time = task_dic["created_time"]
            actual_time = datetime.now()
            seconds_left = (created_time - actual_time).total_seconds() + (minutes_until_execute * 60) # segundos restante para la ejecucion
            message = task_dic["function"][1]

            if seconds_left <= 0:
                # Hora de ejecutar la funcion.
                # Verifico si es asyncrona la funcion y la ejecuto, sino tambien pero sin await
                if (inspect.iscoroutinefunction(task_dic["function"][0])):
                    message.content = task_dic["command"]
                    print(f"Por ejecutar, message.content es: {message.content}")
                    await self.run_task_async(task_dic["function"][0], message)
                else:
                    print("no es asyncrona, ejecutando sincrona")
                    self.run_task(task_dic["function"][0], task_dic["function"][1])

                if loop_times > 0:
                    loop_times -= 1
                    # Actualizo el looptimes en tasks porque sino problemas.
                    self.tasks[self.tasks.index(task_dic)]["loop_times"] = loop_times
                    if loop_times == 0:
                        # Finalizo la task
                        result = self.shizu_database.remove("tasks", {"_id" : task_id})
                        del self.tasks[self.tasks.index(task_dic)]
                        if not result:
                            return print("Error: No se pudo eliminar la tarea de la base de datos.")
                        else:
                            return debug_log("Una task acaba de ser eliminada de la base de datos y de la lista de tasks.", "task")

                # actualizo el proximo tiempo de la tarea
                task_dic["created_time"] = actual_time
                update_task_dic = {
                    "_id" : task_id,
                    "minutes_until_execute" : minutes_until_execute,
                    "loop_times" : loop_times,
                    "created_time" : actual_time
                }

                # Actualizo la task en la base de datos con el nuevo loop_times y el created_time
                modified = self.shizu_database.update_task(update_task_dic)
                if modified:
                    debug_log("[CheckTask] task actualizada exitosamente")
                else:
                    print("ERROR: Se intento actualizar una task en [check_tasks] pero modified es False.")
            else:
                debug_log(f"Task no se ejecuto porque falta tiempo. Hora task creada: {created_time}. Se ejecutara en esa hora mas {minutes_until_execute} minutos.", "tasks")


    async def run_task_async(self, task, *args):
        debug_log("Ejecutando una task asincrona! ...", "tasks")        
        await task(*args)

    def run_task(self, task, *args):
        debug_log("Ejecutando una task sincrona! ...", "tasks")
        task(*args)
