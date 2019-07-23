from bot_vars import DEBUG
from datetime import datetime

def debug_log(text):
    now = datetime.now()
    time = "[%d:%d:%d] " % (now.hour, now.minute, now.second)
    if DEBUG:
        print(time + str(text))
