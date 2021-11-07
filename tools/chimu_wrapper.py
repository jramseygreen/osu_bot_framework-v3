import os
import threading
import random
import json
from itertools import product

import requests

from GAME_ATTR import GAME_ATTR


class Chimu:
    def __init__(self):
        self.url = "https://api.chimu.moe/v1/"

    # fetches a beatmapset dictionary object from chimu.moe
    def fetch_beatmapset(self, beatmapsetID):
        if beatmapsetID:
            url = self.url + "set/" + str(beatmapsetID)
            r = requests.get(url)
            data = json.loads(r.text)
            if data["data"]:
                return data["data"]
            return {}

    # fetches a beatmap dictionary object from chimu.moe
    def fetch_beatmap(self, beatmapID):
        if beatmapID:
            url = self.url + "map/" + str(beatmapID)
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
            if attributes[attribute] != -1:
                url += "&" + attribute + "=" + str(attributes[attribute])
        # print(url)
        r = requests.get(url)
        data = json.loads(r.text)

        # if no error code return data
        if data["code"] == 0:
            return data["data"]
        return []

    # beatmapset download link
    def fetch_set_download_link(self, beatmapsetID, with_video=False):
        if self.fetch_beatmapset(beatmapsetID):
            return self.url + "download/" + str(beatmapsetID) + "?n=" + str(int(with_video))

    # beatmap download link
    def fetch_download_link(self, beatmapID, with_video=False):
        beatmap = self.fetch_beatmap(beatmapID)
        if beatmap:
            beatmapsetID = beatmap["ParentSetId"]
            return self.url + "download/" + str(beatmapsetID) + "?n=" + str(int(with_video))

    # can only download with chimu
    # downloads a beatmapset to the path given, or in the framework directory
    # opening on completion will open it with the default program (osu) and deletes the file on import
    # starts on its own thread by default
    def download_beatmapset(self, beatmapsetID, path="", with_video=False, open_on_complete=False, blocking=False):
        if not blocking:
            x = threading.Thread(target=self.download_beatmapset, args=(beatmapsetID, path, with_video, open_on_complete, True,))
            x.setDaemon(True)
            x.start()
        else:
            if path != "" and path[-1] != "/":
                path = path + "/"
            url = self.fetch_download_link(beatmapsetID, with_video=with_video)
            file = requests.get(url)
            if "Error" not in file.text:
                f = open(path + str(beatmapsetID) + ".osz", "wb")
                f.write(file.content)
                f.close()
                if open_on_complete:
                    # osu will delete the file when it's opened!
                    os.system(path + str(beatmapsetID) + ".osz")

    # takes beatmap id instead of beatmap set id
    def download_beatmap(self, beatmapID, path="", with_video=False, open_on_complete=False, blocking=False):
        beatmap = self.fetch_beatmap(beatmapID)
        if beatmap:
            beatmapsetID = beatmap["ParentSetId"]
            self.download_beatmapset(beatmapsetID, path, with_video, open_on_complete, blocking)

    def fetch_random_beatmap(self, channel=None, **attributes):
        # grab attributes from channel object
        query = ""
        if "query" in attributes:
            query = attributes["query"]
            del attributes["query"]
        if channel:
            attributes = self.channel_to_attributes(channel)

        attributes["amount"] = 10000
        status = None
        if "status" in attributes:
            if type(attributes["status"]) == str:
                attributes["status"] = [attributes["status"]]
            status = attributes["status"]
            if len(status) == 1:
                attributes["status"] = attributes["status"][0]
            else:
                del attributes["status"]
        beatmap_creator_whitelist = []
        beatmap_creator_blacklist = []
        artist_whitelist = []
        artist_blacklist = []
        if "beatmap_creator_whitelist" in attributes:
            beatmap_creator_whitelist = attributes["beatmap_creator_whitelist"]
            del attributes["beatmap_creator_whitelist"]
        if "beatmap_creator_blacklist" in attributes:
            beatmap_creator_blacklist = attributes["beatmap_creator_blacklist"]
            del attributes["beatmap_creator_blacklist"]
        if "artist_whitelist" in attributes:
            artist_whitelist = attributes["artist_whitelist"]
            del attributes["artist_whitelist"]
        if "artist_blacklist" in attributes:
            artist_blacklist = attributes["artist_blacklist"]
            del attributes["artist_blacklist"]

        # fetch beatmap set search results
        beatmapsets = []
        if channel:
            args = [[query], artist_whitelist, beatmap_creator_whitelist]
            if [] in args:
                args.remove([])
            if [""] in args:
                args.remove([""])
            queries = list(product(*args))
            if queries:
                for q in queries:
                    beatmapsets += self.search(" ".join(q).strip(), **attributes)
            else:
                beatmapsets = self.search(query, **attributes)
        else:
            beatmapsets = self.search(query, **attributes)

        # extract beatmaps
        beatmaps = []
        processed = []
        for beatmapset in beatmapsets:
            if beatmapset in processed:
                continue
            processed.append(beatmapset)
            for beatmap in beatmapset["ChildrenBeatmaps"]:

                if status and beatmapset["RankedStatus"] not in status:
                    continue
                elif "mode" in attributes and beatmap["Mode"] != attributes["mode"]:
                    continue
                elif "min_ar" in attributes and attributes["min_ar"] > beatmap["AR"]:
                    continue
                elif "max_ar" in attributes and beatmap["AR"] > attributes["max_ar"]:
                    continue
                elif "min_od" in attributes and attributes["min_od"] > beatmap["OD"]:
                    continue
                elif "max_od" in attributes and beatmap["OD"] > attributes["max_od"]:
                    continue
                elif "min_cs" in attributes and attributes["min_cs"] > beatmap["CS"]:
                    continue
                elif "max_cs" in attributes and beatmap["CS"] > attributes["max_cs"]:
                    continue
                elif "min_hp" in attributes and attributes["min_hp"] > beatmap["HP"]:
                    continue
                elif "max_hp" in attributes and beatmap["HP"] > attributes["max_hp"]:
                    continue
                elif "min_diff" in attributes and attributes["min_diff"] > beatmap["DifficultyRating"]:
                    continue
                elif "max_diff" in attributes and beatmap["DifficultyRating"] > attributes["max_diff"]:
                    continue
                elif "min_bpm" in attributes and attributes["min_bpm"] > beatmap["BPM"]:
                    continue
                elif "max_bpm" in attributes and beatmap["BPM"] > attributes["max_bpm"]:
                    continue
                elif "min_length" in attributes and attributes["min_length"] > beatmap["HitLength"]:
                    continue
                elif "max_length" in attributes and beatmap["HitLength"] > attributes["max_length"]:
                    continue
                elif query and query.lower() not in str(beatmap).lower():
                    continue
                elif channel:
                    if beatmap_creator_whitelist and beatmapset["Creator"].lower() not in beatmap_creator_whitelist and all([x not in beatmap["DiffName"].lower() for x in beatmap_creator_whitelist]):
                        continue
                    elif beatmap_creator_blacklist and beatmapset["Creator"].lower() in beatmap_creator_blacklist:
                        continue
                    elif artist_whitelist and beatmapset["Artist"].lower() not in artist_whitelist:
                        continue
                    elif artist_blacklist and beatmapset["Artist"].lower() in artist_blacklist:
                        continue

                beatmaps.append(beatmap)
        if beatmaps:
            return random.choice(beatmaps)

    def channel_to_attributes(self, channel):
        attributes = {}
        if channel.get_map_status() != ["any"]:
            attributes["status"] = [GAME_ATTR[status] for status in channel.get_map_status()]
        if channel.get_game_mode() != "any":
            attributes["mode"] = GAME_ATTR[channel.get_game_mode()]
        attributes["min_ar"] = channel.get_ar_range()[0]
        attributes["max_ar"] = channel.get_ar_range()[1]
        attributes["min_od"] = channel.get_od_range()[0]
        attributes["max_od"] = channel.get_od_range()[1]
        attributes["min_cs"] = channel.get_cs_range()[0]
        attributes["max_cs"] = channel.get_cs_range()[1]
        attributes["min_hp"] = channel.get_hp_range()[0]
        attributes["max_hp"] = channel.get_hp_range()[1]
        attributes["min_diff"] = channel.get_diff_range()[0]
        if channel.get_diff_range()[1] != -1:
            attributes["max_diff"] = channel.get_diff_range()[1]
        attributes["min_bpm"] = channel.get_bpm_range()[0]
        if channel.get_bpm_range()[1] != -1:
            attributes["max_bpm"] = channel.get_bpm_range()[1]
        attributes["min_length"] = channel.get_length_range()[0]
        if channel.get_length_range()[1] != -1:
            attributes["max_length"] = channel.get_length_range()[1]
        attributes["beatmap_creator_whitelist"] = channel.get_beatmap_creator_whitelist()
        attributes["beatmap_creator_blacklist"] = channel.get_beatmap_creator_blacklist()
        attributes["artist_whitelist"] = channel.get_artist_whitelist()
        attributes["artist_blacklist"] = channel.get_artist_blacklist()
        return attributes
