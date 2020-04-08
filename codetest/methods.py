import inspect
import os


def avoidcalls(func):

    def wrapper(*args):
        # Obtengo el nombre del archivo del metodo que esta llamando
        caller_frame = inspect.stack()[1]
        caller_filename = caller_frame.filename
        caller_filename = os.path.splitext(os.path.basename(caller_filename))[0]

        # Obtengo el nombre del archivo del metodo que se llama
        called_filename = func.__module__

        if called_filename == caller_filename:
            func(*args)
        else:
            print("Ignorando llamada externa")

    return wrapper


class Method:

    def First(self):
        print("============================")

        self.Second()
        print("============================\n")

    @avoidcalls
    def Second(self) -> str:
        print("============================")
        currFrame = inspect.currentframe().f_back
        calFrame = inspect.getouterframes(currFrame, 1)
        #print(inspect.stack())
        #print(currFrame)
        #print(calFrame)
        #print(self.Second.__self__.__class__.__name__)
        print(self.Second.__qualname__)
        print("============================\n")
        return ""


