import time
from datetime import datetime
import inspect
from threading import Timer
import bot_vars
import Debug

class ShizuTasks():

    tasks = []


    def __init__(self):
        pass

    def create_task2(self, loop_minutes, message, function, *args):
        tasks_d = {
            "task_name": inspect.stack()[1].funcion, # como nombre le coloco el nombre de la funcion que llamo al metodo createtask
            "user_task": message.author.id,
            "guild_id": message.guild.id,
            "channel_id": message.channel.id,
            "loop_minutes": loop_minutes,
            "task_created_time": datetime.now(), #datetime.now()
            "method": [function, *args] # function, *args
        }
        self.tasks.append(tasks_d)

    def create_task(self, loop_minutes, function, *args):
        task_created_time = datetime.now()
        # el tiempo en que se creo la task debe re setearse cada vez que se ejecuta la task
        print("Task creada!")
        self.tasks.append([[function, *args], loop_minutes, task_created_time])

    async def check_tasks(self):
        for task in self.tasks:
            loop_minutes = task[1]
            task_created_time = task[2]
            actual_minutes = datetime.now().hour * 60 + datetime.now().minute # tiempo, en minutos, que transcurrio en el dia al momento de ejecutar esto
            execution_deadline = loop_minutes + task_created_time.minute + task_created_time.hour * 60 # tiempo, en minutos, en que debe ejecutarse la funcion

            # si el dia en que se creo la task NO es hoy, continuo a la siguiente tarea
            if task_created_time.day != datetime.now().day:
                if bot_vars.DEBUG:
                    Debug.log("Task no se ejecuto porque distinto dia. Hora task creada: {1}. Hora de ejecucion de la task: {0}: ".format(task_created_time, execution_deadline))
                continue
            else: # es hoy, verifico los minutos

                # Si el tiempo que paso en el dia hasta ahora supera al tiempo en que debe ejecutarse la funcion, pues la ejecuto
                if actual_minutes >= execution_deadline:
                        
                    # Verifico si es asyncrona la funcion y la ejecuto, sino tambien pero sin await
                    if (inspect.iscoroutinefunction(task[0][0])):
                        await self.run_task_async(task[0][0], task[0][1]) # task[0][0], task[0][1] ===> function, *args
                    else:
                        print("no es asyncrona, ejecutando no asayncrona")
                        self.run_task(task[0])

                    # actualizo el proximo tiempo de la tarea
                    task[2] = datetime.now()
                else:
                    if bot_vars.DEBUG:
                        Debug.log("Task no se ejecuto porque falta tiempo. Hora task creada: {1}. Hora de ejecucion de la task: {0}: ".format(task_created_time, execution_deadline))


    async def run_task_async(self, task, *args):
        if bot_vars.DEBUG:
            Debug.log("Ejecutando una task asincrona! ...")        
        await task(*args)

    def run_task(self, task, *args):
        if bot_vars.DEBUG:
            Debug.log("Ejecutando una task sincrona! ...")
        task(*args)
