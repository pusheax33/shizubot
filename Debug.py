from datetime import datetime


def log(message):
    time = "[{0}:{1}] ".format(datetime.now().hour.__str__(), datetime.now().minute.__str__())
    print(time + message)
