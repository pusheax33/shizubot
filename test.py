from image_download import googleimagesdownload
import time
import random

def img(message):
    image_to_search = message

    arguments = {
                 "keywords": image_to_search,
                 "no_download": True,
                 "limit": 1,
                 "silent_mode": True
                 }

    response = googleimagesdownload()
    paths = response.download(arguments)
    image_url = paths[0][image_to_search][0]

def gif(message):
    image_to_search = message
    gif_position = random.randrange(0, 10)
    arguments = {
                 "keywords": image_to_search,
                 "no_download": True,
                 "silent_mode": True,
                 "limit": gif_position,
                 "format": "jpg, png, bmp",
                 "offset": gif_position
    }
    resp = googleimagesdownload()
    paths = resp.download(arguments)

    print(paths)


def tes():
    gimg = googleimagesdownload()
    args = {
        "keywords": "osos",
        "limit": 1,
        "no_download": True
        }

    resp = gimg.download(args)
    print("ASDADASDSADASDAS")
    print(resp[0]["osos"][0])

while(True):
    time.sleep(0.5)
    gif("gatos")
