import json
import threading
import time

from GAME_ATTR import GAME_ATTR
from channel import Channel
import requests
from requests.structures import CaseInsensitiveDict


class Game(Channel):
    def __init__(self, bot, channel, verbose):
        super().__init__(bot, channel, verbose)
        self.__creator = ""
        self.__invite_link = ""
        self.__slots = {i: {"username": "", "team": "", "score": {}} for i in range(16)}
        self.__host = ""
        self.__in_progress = False
        self.__beatmap = None # osu tutorial as default 22538
        self.__match_history = self.fetch_match_history()
        self.__size = 8
        self.__password = ""
        self.__title = ""
        self.__welcome_message = ""
        self.__commands = {"!info": {"response": "Created with osu_bot_framework v3", "description": "Created with osu_bot_framework v3"}}
        self.__referees = [bot.get_username()]
        self.__config_link = ""
        self.__config_text = ""

        # limits and ranges (done)
        self.__ar_range = (0.0, 10.0)
        self.__od_range = (0.0, 10.0)
        self.__cs_range = (0.0, 10.0)
        self.__hp_range = (0.0, 10.0)
        self.__diff_range = (0.0, -1.0)
        self.__bpm_range = (0.0, -1.0)
        self.__length_range = (0, -1)
        self.__map_status = ["any"]

        # game attributes
        self.__mods = ["ANY"]
        self.__scoring_type = "any"
        self.__team_type = "any"
        self.__game_mode = "any"

        # on_event methods
        self.__on_match_start_method = None
        self.__on_match_finish_method = None
        self.__on_match_abort_method = None
        self.__on_host_change_method = None
        self.__on_beatmap_change_method = None
        self.__on_changing_beatmap_method = None
        self.__on_all_players_ready_method = None
        self.__on_room_close_method = None
        self.__on_slot_change_method = None
        self.__on_team_change_method = None
        self.__on_team_addition_method = None
        self.__on_clear_host_method = None

    def process_message(self, message):
        super().process_message(message)
        # update room attributes
        if message["username"] == "BanchoBot":
            if "joined in slot" in message["content"]:
                username = message["content"][:message["content"].find("joined") - 1]
                team = ""
                if "for team blue" in message["content"]:
                    team = "blue"
                elif "for team red" in message["content"]:
                    team = "red"
                if self.__on_team_addition_method:
                    threading.Thread(target=self.__on_team_addition_method, args=(username, team,)).start()
                self.set_slot(int(message["content"].split("slot ", 1)[1].split(".", 1)[0].split(" ")[0]) - 1, {"username": username, "team": team, "score": {}})
                self.add_user(username)
            elif "left the game" in message["content"]:
                username = message["content"][:message["content"].find("left") - 1]
                self.del_user(username)
            elif "moved to slot" in message["content"]:
                slot = int(message["content"].split(" ")[-1]) - 1
                username = message["content"].replace(" moved to slot " + str(slot + 1), "")
                team = self.get_team(username)
                score = self.get_score(username)
                self.set_slot(slot, {"username": username, "team": team, "score": score})
                if self.__on_slot_change_method:
                    threading.Thread(target=self.__on_slot_change_method, args=(username, slot,)).start()
            elif "changed to Blue" in message["content"]:
                username = message["content"].replace(" changed to Blue", "")
                slot = self.get_slot_num(username)
                self.set_slot(slot, {"username": username, "team": "blue", "score": {}})
                if self.__on_team_change_method:
                    threading.Thread(target=self.__on_team_change_method, args=(username, "blue",)).start()
            elif "changed to Red" in message["content"]:
                username = message["content"].replace(" changed to Red", "")
                slot = self.get_slot_num(username)
                self.set_slot(slot, {"username": username, "team": "red", "score": {}})
                if self.__on_team_change_method:
                    threading.Thread(target=self.__on_team_change_method, args=(username, "red",)).start()
            elif "became the host" in message["content"]:
                self.set_host(message["content"].replace(" became the host.", ""))
            elif "The match has started!" == message["content"]:
                self.__in_progress = True
                self.__check_attributes()
            elif "The match has finished!" == message["content"]:
                self.__in_progress = False
                self.__fetch_scores()
                if self.__on_match_finish_method:
                    threading.Thread(target=self.__on_match_finish_method).start()
            elif "Aborted the match" == message["content"]:
                self.__in_progress = False
            elif "Beatmap changed to" in message["content"] or "Changed beatmap to" in message["content"]:
                beatmapID = message["content"].split("/b/", 1)[1].split(" ", 1)[0].replace(")", "")
                self.__check_beatmap(self.fetch_beatmap(beatmapID))
            elif "Host is changing map..." == message["content"]:
                if self.__on_changing_beatmap_method:
                    threading.Thread(target=self.__on_changing_beatmap_method).start()
            elif "All players are ready" == message["content"]:
                if self.__on_all_players_ready_method:
                    threading.Thread(target=self.__on_all_players_ready_method).start()
            elif "Closed the match" == message["content"]:
                self._bot.part(self._channel)
                if self.__on_room_close_method:
                    threading.Thread(target=self.__on_room_close_method).start()
            elif "Cleared match host" == message["content"]:
                if self.__on_clear_host_method:
                    threading.Thread(target=self.__on_clear_host_method, args=(self.__host,)).start()
                self.__host = ""

        elif message["username"] in [x.replace(" ", "_") for x in self.__referees]:
            message_arr = message["content"].lower().split(" ")
            if len(message_arr) >= 2:
                command = " ".join(message_arr[:2]).strip()
                args = message_arr[2:]
                if message["username"] == self.__creator.replace(" ", "_"):
                    if command == "!mp addref":
                        self.__referees += args
                    elif command == "!mp removeref":
                        for username in args:
                            self.__referees.remove(username)
                if command == "!mp password":
                    self.__invite_link = self.__invite_link.replace(self.__password, "")
                    if args:
                        self.__password = args[0]
                        self.__invite_link = self.__invite_link + args[0]
                    else:
                        self.__password = ""
                elif command == "!mp size":
                    if args:
                        self.__size = int(args[0])
                elif command == "!mp abort":
                    if self.__on_match_abort_method:
                        threading.Thread(target=self.__on_match_abort_method).start()

        self.__execute_commands(message)

    def __execute_commands(self, message):
        command = message["content"].split(" ", 1)[0]
        if command in self.__commands:
            if callable(self.__commands[command]["response"]):
                threading.Thread(target=self.__commands[command]["response"], args=(message,)).start()
            else:
                self.send_message(self.__commands[command]["response"])

    def send_message(self, message):
        super().send_message(message)
        self.__execute_commands({"username": self._bot.get_username(), "channel": self._channel, "content": message})

    def del_user(self, username):
        # remove from slots
        for slot in self.__slots:
            if self.__slots[slot]["username"] == username:
                self.__slots[slot] = {"username": "", "team": "", "score": {}}
                break
        super().del_user(username)

    def add_user(self, username):
        super().add_user(username)
        # welcome message implementation
        if self.__welcome_message:
            self._bot.send_personal_message(username.replace(" ", "_"), self.__welcome_message)

    def close(self):
        self.send_message("!mp close")
        self._bot.part(self._channel)

    def fetch_match_history(self):
        url = "https://osu.ppy.sh/community/matches/" + self._channel[4:]

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"

        r = requests.get(url, headers=headers)
        return json.loads(r.text)

    def get_match_history(self):
        return self.__match_history

    # fetches the most recent match data from ppy.sh
    def get_match_data(self):
        for event in reversed(self.get_match_history()["events"]):
            if "game" in event:
                return event["game"]
        return {}

    def fetch_beatmap(self, beatmapID):
        if self.__beatmap:
            if beatmapID == self.__beatmap["id"]:
                return self.__beatmap
        if int(beatmapID) == 0:
            return {}
        url = "https://osu.ppy.sh/b/" + str(beatmapID)
        r = requests.get(url)
        beatmapset = {}
        try:
            beatmapset = json.loads(
                r.text.split('<script id="json-beatmapset" type="application/json">\n        ', 1)[1].split(
                    "\n", 1)[0])
        except:
            return {}
        if "beatmaps" in beatmapset:
            for beatmap in beatmapset["beatmaps"]:
                if beatmap["id"] == int(r.url.split("/")[-1]):
                    return beatmap
        return {}

    # fetches a beatmapset associated with a beatmapID from ppy.sh
    def fetch_beatmapset(self, beatmapID):
        if int(beatmapID) == 0:
            return {}
        url = "https://osu.ppy.sh/b/" + str(beatmapID)
        r = requests.get(url)
        try:
            return json.loads(
                r.text.split('<script id="json-beatmapset" type="application/json">\n        ', 1)[1].split(
                    "\n", 1)[0])
        except:
            return {}

    def __fetch_scores(self):
        self.__match_history = self.fetch_match_history()
        for score in self.get_match_data()["scores"]:
            self.__slots[score["match"]["slot"]]["score"] = score

    def get_score(self, username):
        return self.get_slot(username)["score"]

    def get_scores(self):
        scores = []
        for slot in self.__slots:
            if self.__slots[slot]["score"]:
                scores.append(self.__slots[slot]["score"])
        return scores

    def __check_beatmap(self, beatmap, running=False):
        if not running:
            threading.Thread(target=self.__check_beatmap, args=(beatmap, True,)).start()
        else:
            if self.verbose:
                print("-- Beatmap checker started --")
            revert = False
            if not beatmap:
                self.send_message("The selected beatmap is not submitted! Can't check attributes.")
                revert = False
            elif beatmap["id"] == 22538:
                revert = False
            elif beatmap == self.__beatmap:
                return
            elif self.__od_range[0] > beatmap["accuracy"] > self.__od_range[1]:
                self.send_message(
                    self.__host + " the selected beatmap is outside the overall difficulty range: " + str(
                        self.__od_range))
                revert = True
            elif self.__ar_range[0] > beatmap["ar"] > self.__ar_range[1]:
                self.send_message(self.__host + " the selected beatmap is outside the approach rate range: " + str(
                    self.__ar_range))
                revert = True
            elif self.__bpm_range[0] > beatmap["bpm"] or (
                        self.__bpm_range[1] != -1 and self.__bpm_range[1] < beatmap["bpm"]):
                self.send_message(
                    self.__host + " the selected beatmap is outside the BPM range: " + str(self.__bpm_range).replace("-1.0", "unlimited"))
                revert = True
            elif self.__cs_range[0] > beatmap["cs"] > self.__cs_range[1]:
                self.send_message(
                    self.__host + " the selected beatmap is outside the circle size range: " + str(self.__cs_range))
                revert = True
            elif self.__hp_range[0] > beatmap["drain"] > self.__hp_range[1]:
                self.send_message(
                    self.__host + " the selected beatmap is outside the HP range: " + str(self.__hp_range))
                revert = True
            elif self.__length_range[0] > beatmap["hit_length"] or (
                    self.__length_range[1] != -1 and self.__length_range[1] < beatmap["hit_length"]):
                if self.__length_range[1] == -1:
                    self.send_message(self.__host + " the selected beatmap is outside the length range: " + str(
                        [str(x // 60) + "min, " + str(x % 60) + "sec" for x in [self.__length_range[0]]] + ["unlimited"]))
                else:
                    self.send_message(self.__host + " the selected beatmap is outside the length range: " + str(
                        [str(x // 60) + "min, " + str(x % 60) + "sec" for x in self.__length_range]))
                revert = True
            elif self.__map_status != ["any"] and beatmap["status"] not in self.__map_status:
                self.send_message(self.__host + " the selected beatmap must be: " + " or ".join(self.__map_status))
                revert = True
            elif beatmap["difficulty_rating"] < self.__diff_range[0] or (beatmap["difficulty_rating"] > self.__diff_range[1] != -1):
                self.send_message(self.__host + " the selected beatmap is outside the difficulty range: " + str(self.__diff_range).replace("-1.0", "unlimited") + "*")
                revert = True

            if revert:
                self.set_beatmap(self.__beatmap)
            else:
                if self.__on_beatmap_change_method:
                    threading.Thread(target=self.__on_beatmap_change_method, args=(self.__beatmap, beatmap,)).start()
                self.__beatmap = beatmap

    def __check_attributes(self, running=False):
        if not running:
            threading.Thread(target=self.__check_attributes, args=(True,)).start()
        else:
            if self.verbose:
                print("-- Attribute checker started --")
            self.__match_history = self.fetch_match_history()
            match = self.get_match_data()
            abort = False

            if self.__scoring_type.lower() != "any" and match["scoring_type"] != self.__scoring_type.lower():
                self.send_message(self.__host + " the allowed scoring type is: " + self.__scoring_type)
                abort = True
            elif self.__mods != ["ANY"]:
                if "FREEMOD" in self.__mods and match["mods"] != []:
                    self.send_message(self.__host + " the allowed mods are: " + ", ".join(self.__mods))
                    abort = True
                if self.__mods != ["FREEMOD"] and (not all([mod in self.__mods for mod in match["mods"]]) or not all([mod in match["mods"] for mod in self.__mods])):
                    self.send_message(self.__host + " the allowed mods are: " + ", ".join(self.__mods))
                    abort = True
            elif self.__team_type != "any" and self.__team_type.lower() != match["team_type"]:
                self.send_message(self.__host + " the allowed team types are: " + " or ".join(self.__team_type))
                abort = True

            if abort:
                # execute on_rule_break
                self.send_message("!mp abort")
                self.send_message("!mp set " + str(GAME_ATTR[self.__team_type[0]]) + " " + str(GAME_ATTR[self.__scoring_type[0]]) + " " + str(self.__size))
                beatmapID = str(self.__beatmap["id"])
                if not self.__beatmap:
                    beatmapID = "22538"
                self.send_message("!mp map " + beatmapID + " " + str(GAME_ATTR[self.__game_mode[0]]))
                self.send_message("!mp mods " + " ".join(self.__mods))
            elif self.__on_match_start_method:
                threading.Thread(target=self.__on_match_start_method).start()

    def abort_match(self):
        self.send_message("!mp abort")
        if self.__on_match_abort_method:
            threading.Thread(target=self.__on_match_abort_method).start()

    def start_match(self):
        self.send_message("!mp start")

    def in_progress(self):
        return self.__in_progress

    def set_invite_link(self, link):
        self.__invite_link = link

    def get_invite_link(self):
        return self.__invite_link

    def get_slots(self):
        return self.__slots

    def set_slot(self, slot, data):
        for s in self.__slots:
            if self.__slots[s] == data:
                self.__slots[s] = {"username": "", "team": "", "score": {}}
        self.__slots[slot] = data

    def get_slot(self, username):
        for slot in self.__slots:
            if self.__slots[slot]["username"] == username:
                return self.__slots[slot]

    def get_slot_num(self, username):
        for i in range(16):
            if self.__slots[i]["username"] == username:
                return i

    def get_red_team(self):
        users = []
        for slot in self.__slots:
            if self.__slots[slot]["team"] == "red":
                users.append(self.__slots[slot]["username"])
        return users

    def get_blue_team(self):
        users = []
        for slot in self.__slots:
            if self.__slots[slot]["team"] == "blue":
                users.append(self.__slots[slot]["username"])
        return users

    def get_team(self, username):
        if username in self.get_blue_team():
            return "blue"
        if username in self.get_red_team():
            return "red"
        return ""

    def get_host(self):
        return self.__host

    def set_host(self, username):
        if self.__on_host_change_method:
            threading.Thread(target=self.__on_host_change_method, args=(self.__host, username,)).start()
        self.__host = username

    def set_password(self, password):
        self.__invite_link = self.__invite_link.replace(self.__password, "")
        self.__password = password
        self.__invite_link = self.__invite_link + password
        self.send_message("!mp password " + self.__password)

    def get_password(self):
        return self.__password

    def add_command(self, command, response, description=""):
        self.__commands[command] = {"response": response, "description": description}

    def del_command(self, command):
        if command in self.__commands:
            del self.__commands[command]

    def get_commands(self):
        return self.__commands

    def has_command(self, command):
        return command in self.__commands

    def add_referee(self, username):
        if username not in self.__referees:
            self.__referees.append(username)

    # grabs existing users, the room creator, and adds creator to referee list
    def get_existing_attributes(self):
        self.__title = self.__match_history["match"]["name"]
        for user in self.__match_history["users"]:
            self.add_user(user["username"])
        self.__creator = self._bot.fetch_user_profile(self.__match_history["events"][0]["user_id"])["username"]
        self.add_referee(self.__creator)

    def set_beatmap(self, beatmap):
        self.__beatmap = beatmap
        if beatmap:
            self.send_message("!mp map " + str(beatmap["id"]))
        else:
            self.send_message("!mp map 22538")

    def get_beatmap(self):
        return self.__beatmap

    # getters and setters for limits and ranges
    # sets the allowed map statuses
    def set_map_status(self, status):
        if type(status) == list:
            self.__map_status = [x.lower() for x in status]
        else:
            self.__map_status = [status.lower()]

    # returns the allowed map statuses
    def get_map_status(self):
        return self.__map_status

    # sets the allowed difficulty range
    def set_diff_range(self, range):
        self.__diff_range = (float(range[0]), float(range[1]))

    # returns the allowed difficulty range
    def get_diff_range(self):
        return self.__diff_range

    # sets the allowed mods
    def set_mods(self, mods):
        if type(mods) == list:
            mods = [mod.upper() for mod in mods]
        else:
            mods = [mods.upper()]
        self.__mods = mods
        self.send_message("!mp mods " + " ".join(self.__mods))

    # gets the allowed mods
    def get_mods(self):
        return self.__mods

    # sets the allowed approach rate range
    def set_ar_range(self, range):
        self.__ar_range = (float(range[0]), float(range[1]))

    # returns the allowed approach rate range
    def get_ar_range(self):
        return self.__ar_range

    # sets the allowed overall difficulty range
    def set_od_range(self, range):
        self.__od_range = (float(range[0]), float(range[1]))

    # gets the allowed overall difficulty range
    def get_od_range(self):
        return self.__od_range

    # sets the allowed circle size range
    def set_cs_range(self, range):
        self.__cs_range = (float(range[0]), float(range[1]))

    # gets the allowed circle size range
    def get_cs_range(self):
        return self.__cs_range

    # sets the allowed hp range
    def set_hp_range(self, range):
        self.__hp_range = (float(range[0]), float(range[1]))

    # gets the allowed hp range
    def get_hp_range(self):
        return self.__hp_range

    # sets the allowed bpm range
    def set_bpm_range(self, range):
        self.__bpm_range = (float(range[0]), float(range[1]))

    # returns the allowed bpm range
    def get_bpm_range(self):
        return self.__bpm_range

    # sets the allowed beatmap length range
    def set_length_range(self, range):
        self.__length_range = (int(range[0]), int(range[1]))

    # returns the allowed beatmap length range
    def get_length_range(self):
        return self.__length_range

    # todo
    # sets the allowed room scoring types
    def set_scoring_type(self, scoring_type):
        self.__scoring_type = scoring_type.lower()
        self.send_message("!mp set scoremode " + str(GAME_ATTR[self.__scoring_type]))

    # returns the scoring type of the room
    def get_scoring_type(self):
        return self.__scoring_type

    # sets the team type of the room
    def set_team_type(self, team_type):
        self.__team_type = team_type.lower()
        if self.__team_type != "any":
            self.send_message("!mp set " + str(GAME_ATTR[self.__team_type]))

    # returns the tracked team type of the room
    def get_team_type(self):
        return self.__team_type

    # sets the tracked game mode
    def set_game_mode(self, mode):
        self.__game_mode = mode.lower()
        if self.__game_mode != "any":
            self.send_message("!mp map " + str(self.__beatmap["id"]) + " " + str(GAME_ATTR[self.__game_mode]))

    # returns the game mode of the room
    def get_game_mode(self):
        return self.__game_mode

    def set_title(self, title):
        self.__title = title

    def get_title(self):
        return self.__title

    def set_welcome_message(self, message):
        self.__welcome_message = message

    def get_welcome_message(self):
        return self.__welcome_message

    def set_size(self, size):
        self.__size = int(size)
        self.send_message("!mp size " + str(size))

    def get_size(self):
        return self.__size

    # returns the link to the current room configuration and uploads to paste2.org if the configuration has changed
    def get_config_link(self):
        text = " 𝙶̲𝚊̲𝚖̲𝚎̲ ̲𝚁̲𝚘̲𝚘̲𝚖̲ ̲𝙲̲𝚘̲𝚗̲𝚏̲𝚒̲𝚐̲𝚞̲𝚛̲𝚊̲𝚝̲𝚒̲𝚘̲𝚗̲:"
        text += "\n     • Title: " + self.__title
        text += "\n     • Channel: " + self._channel
        text += "\n     • Match history: https://osu.ppy.sh/mp/" + self._channel.replace("#mp_", "", 1) + "/"
        text += "\n     • Invite link: " + self.__invite_link
        text += "\n     • Admins/Refs: " + ", ".join(self.__referees)
        text += "\n     • Welcome message: " + self.__welcome_message
        text += "\n\n 𝙶̲𝚊̲𝚖̲𝚎̲ ̲𝚛̲𝚘̲𝚘̲𝚖̲ ̲𝚊̲𝚝̲𝚝̲𝚛̲𝚒̲𝚋̲𝚞̲𝚝̲𝚎̲𝚜̲:"
        text += "\n     • Room size: " + str(self.__size)
        text += "\n     • game mode: " + self.__game_mode
        text += "\n     • scoring mode: " + self.__scoring_type
        text += "\n     • team mode: " + self.__team_type
        text += "\n     • mods: " + ", ".join(self.__mods)
        text += "\n     • beatmap status: " + ", ".join(self.__map_status)
        text += "\n     • Difficulty rating range: " + str(self.__diff_range)
        text += "\n     • Approach rate range: " + str(self.__ar_range)
        text += "\n     • Overall difficulty range: " + str(self.__od_range)
        text += "\n     • Circle size range: " + str(self.__cs_range)
        text += "\n     • HP range: " + str(self.__hp_range)
        text += "\n     • BPM range: " + str(self.__bpm_range)
        text += "\n     • Beatmap length range: " + str(self.__length_range)
        if self.__length_range[1] == -1:
            length_range = [self.__length_range[0]]
            text += " " + str([str(x // 60) + "min, " + str(x % 60) + "sec" for x in length_range] + ["unlimited"])
        else:
            text += " " + str([str(x // 60) + "min, " + str(x % 60) + "sec" for x in self.__length_range])

        text += "\n\n 𝙲̲𝚘̲𝚖̲𝚖̲𝚊̲𝚗̲𝚍̲𝚜̲:"
        for command in self.__commands:
            text += "\n     • " + command + ": " + self.__commands[command]["description"]

        text += "\n\n 𝚃̲𝚑̲𝚎̲ ̲𝚏̲𝚘̲𝚕̲𝚕̲𝚘̲𝚠̲𝚒̲𝚗̲𝚐̲ ̲𝚖̲𝚎̲𝚜̲𝚜̲𝚊̲𝚐̲𝚎̲𝚜̲ ̲𝚊̲𝚛̲𝚎̲ ̲𝚋̲𝚎̲𝚒̲𝚗̲𝚐̲ ̲𝚋̲𝚛̲𝚘̲𝚊̲𝚍̲𝚌̲𝚊̲𝚜̲𝚝̲ ̲𝚘̲𝚗̲ ̲𝚊̲ ̲𝚝̲𝚒̲𝚖̲𝚎̲𝚛̲:"
        text += "\n\n     𝙸̲𝙳̲   𝙼̲𝚎̲𝚜̲𝚜̲𝚊̲𝚐̲𝚎̲"
        for broadcast in self._bot.get_broadcast_controller().get_broadcasts(self._channel):
            text += "\n     " + str(broadcast["id"]) + "    '" + broadcast["message"] + "'"
        if text != self.__config_text:
            self.__config_text = text
            self.__config_link = self._bot.paste2_upload("Room configuration for " + self._channel, text)
        return self.__config_link

    def on_match_start(self, method=None):
        self.__on_match_start_method = method

    def on_match_finish(self, method=None):
        self.__on_match_finish_method = method

    def on_match_abort(self, method):
        self.__on_match_abort_method = method

    def on_all_players_ready(self, method):
        self.__on_all_players_ready_method = method

    def on_host_change(self, method):
        self.__on_host_change_method = method

    def on_beatmap_change(self, method):
        self.__on_beatmap_change_method = method

    def on_changing_beatmap(self, method):
        self.__on_changing_beatmap_method = method

    def on_room_close(self, method):
        self.__on_room_close_method = method

    def on_slot_change(self, method):
        self.__on_slot_change_method = method

    def on_team_change(self, method):
        self.__on_team_change_method = method

    def on_team_addition(self, method):
        self.__on_team_addition_method = method

    def on_clear_host(self, method):
        self.__on_clear_host_method = method
        
    def implement_logic_profile(self, profile):
        profile = self._bot.get_logic_profile(profile)(self._bot, self)
        if hasattr(profile, "on_personal_message") and callable(getattr(profile, "on_personal_message")):
            self.on_personal_message(profile.on_personal_message)
        if hasattr(profile, "on_join") and callable(getattr(profile, "on_join")):
            self.on_join(profile.on_join)
        if hasattr(profile, "on_part") and callable(getattr(profile, "on_part")):
            self.on_part(profile.on_part)
        if hasattr(profile, "on_message") and callable(getattr(profile, "on_message")):
            self.on_message(profile.on_message)
            
        if hasattr(profile, "on_match_start") and callable(getattr(profile, "on_match_start")):
            self.on_match_start(profile.on_match_start)
        if hasattr(profile, "on_match_finish") and callable(getattr(profile, "on_match_finish")):
            self.on_match_finish(profile.on_match_finish)
        if hasattr(profile, "on_host_change") and callable(getattr(profile, "on_host_change")):
            self.on_host_change(profile.on_host_change)
        if hasattr(profile, "on_team_addition") and callable(getattr(profile, "on_team_addition")):
            self.on_team_addition(profile.on_team_addition)
        if hasattr(profile, "on_team_change") and callable(getattr(profile, "on_team_change")):
            self.on_team_change(profile.on_team_change)
        if hasattr(profile, "on_slot_change") and callable(getattr(profile, "on_slot_change")):
            self.on_slot_change(profile.on_slot_change)
        if hasattr(profile, "on_all_players_ready") and callable(getattr(profile, "on_all_players_ready")):
            self.on_all_players_ready(profile.on_all_players_ready)
        if hasattr(profile, "on_beatmap_change") and callable(getattr(profile, "on_beatmap_change")):
            self.on_beatmap_change(profile.on_beatmap_change)
        if hasattr(profile, "on_changing_beatmap") and callable(getattr(profile, "on_changing_beatmap")):
            self.on_changing_beatmap(profile.on_changing_beatmap)
        if hasattr(profile, "on_room_close") and callable(getattr(profile, "on_room_close")):
            self.on_room_close(profile.on_room_close)
        if hasattr(profile, "on_clear_host") and callable(getattr(profile, "on_clear_host")):
            self.on_clear_host(profile.on_clear_host)

    def get_attributes(self):
        data = super().get_attributes()
        data["creator"] = self.__creator
        data["invite_link"] = self.__invite_link
        data["slots"] = self.__slots
        data["host"] = self.__host
        data["in_progress"] = self.__in_progress
        data["beatmap"] = self.__beatmap
        data["size"] = self.__size
        data["password"] = self.__password
        data["title"] = self.__title
        data["welcome_message"] = self.__welcome_message
        data["commands"] = self.__commands
        data["referees"] = self.__referees
        data["config_link"] = self.__config_link

        # limits and ranges (done)
        data["ar_range"] = self.__ar_range
        data["od_range"] = self.__od_range
        data["cs_range"] = self.__cs_range
        data["hp_range"] = self.__hp_range
        data["diff_range"] = self.__diff_range
        data["bpm_range"] = self.__bpm_range
        data["length_range"] = self.__length_range
        data["map_status"] = self.__map_status

        # game attributes
        data["mods"] = self.__mods
        data["scoring_type"] = self.__scoring_type
        data["team_type"] = self.__team_type
        data["game_mode"] = self.__game_mode

        return data