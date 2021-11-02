import requests
import json


class Chimu:
    def __init__(self):
        self.url = "https://api.chimu.moe/v1/"

    # fetches a beatmapset dictionary object from chimu.moe
    def fetch_beatmapset(self, beatmapsetID):
        if beatmapsetID:
            url = self.url + str(beatmapsetID)
            r = requests.get(url)
            data = json.loads(r.text)
            if data["data"]:
                return data["data"]
            return {}

    # fetches a beatmap dictionary object from chimu.moe
    def fetch_beatmap(self, beatmapID):
        if beatmapID:
            url = self.url + str(beatmapID)
            r = requests.get(url)
            data = json.loads(r.text)
            if data["data"]:
                return data["data"]
            return {}

    # return list of beatmapsets based on query + provided attributes
    def search(self, query="", **attributes):
        # construct url
        url = self.url + "search?query=" + query.replace(" ", "%20")
        for attribute in attributes:
            url += "&" + attribute + "=" + attributes[attribute]

        r = requests.get(url)
        data = json.loads(r.text)

        # if no error code return data
        if data["code"] == 0:
            return data["data"]
        return []

    def fetch_random_beatmap(self, channel=None, **attributes):
        pass
