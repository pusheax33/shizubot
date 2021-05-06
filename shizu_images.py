import aiohttp
from bot_vars import BING_API_KEY, BING_ENDPOINT, COMMAND_PREFIX
from decorators import commands
import random


class ImageSearch:

    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY,
               "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
               "cookie" : "SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=DC04B2DF95F64D13BDBCB72CADC35190&dmnchg=1; _SS=SID=1A151521D50D6D9A30291BBDD4846C73; _HPVN=CS=eyJQbiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMC0wMy0yOVQwMDowMDowMFoiLCJJb3RkIjowLCJEZnQiOm51bGwsIk12cyI6MCwiRmx0IjowLCJJbXAiOjF9; _EDGE_V=1; MUID=35BE80C6B2AF67D736CB8E5AB3266652; MUIDB=35BE80C6B2AF67D736CB8E5AB3266652; _EDGE_S=mkt=es-ar&ui=es-es&F=1&SID=1A151521D50D6D9A30291BBDD4846C73; ipv6=hit=1585517609184&t=6; SRCHUSR=DOB=20200329&T=1585514012000; imgv=lts=20200329; SRCHHPGUSR=HV=1585514016&WTS=63721110806&CW=1232&CH=150&DPR=1&UTC=-180"}

    async def fetch(self, url, params=None):
        async with aiohttp.ClientSession(headers=self.headers) as client:
            async with client.get(url, params=params) as resp:
                try:
                    resp.raise_for_status()
                    return resp
                except Exception:
                    print("ERROR AL FETCH")
                    return None

    async def fetch_json(self, url, params=None):
        async with aiohttp.ClientSession(headers=self.headers) as client:
            async with client.get(url, params=params) as resp:
                try:
                    resp.raise_for_status()
                    return await resp.json()
                except Exception:
                    print("ERROR AL FETCH")
                    return None

    async def fetch_bytes(self, url, params=None):
        """
            :param url: link de donde se descargara
            :param params: parametros requeridos por el get
            :return: Devuelve la response en formato byte para su guardado.
        """
        async with aiohttp.ClientSession(headers=self.headers) as client:
            async with client.get(url, params=params) as resp:
                try:
                    resp.raise_for_status()
                    return await resp.read()
                except Exception:
                    print("ERROR AL FETCH")
                    return None


class ShizuImage:

    def __init__(self):
        self.image_search = ImageSearch()

    @commands()
    async def img(self, message, imageType = None):
        img_to_search = message.content
        params = {"q": img_to_search, "imageType": imageType}
        if not imageType:
            params = {"q": img_to_search}

        if message.channel.is_nsfw():
            params["safeSearch"] = "Off"

        response = await self.image_search.fetch_json(BING_ENDPOINT + "/images/search", params)
        if not response:
            return await message.channel.send("Hubo un error al obtener las imagenes!")
        thumbnail_urls = [img["contentUrl"] for img in response["value"]]

        if len(thumbnail_urls) == 0:
            return await message.channel.send("No pude encontrar nada!")
        else:
            choosed_image = random.choice(thumbnail_urls)
            await message.channel.send(choosed_image)

    @commands()
    async def gif(self, message):
        message.content = COMMAND_PREFIX+"img " + message.content
        await self.img(message, "AnimatedGif")

