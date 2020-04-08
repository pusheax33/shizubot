from methods import Method
import inspect


class MethodCaller:

    def __init__(self):
        self.method = Method()

    def start(self):
        data = inspect.getmembers(self.method, predicate=inspect.ismethod)
        #print(data)
        for name, method, in data:
            #print(name)
            #print(method)
            if name == "__init__":
                continue

            method()


MethodCaller().start()
