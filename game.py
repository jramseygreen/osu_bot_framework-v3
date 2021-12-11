import inspect
import json
import threading
import time

from GAME_ATTR import GAME_ATTR, TUTORIAL
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
        # osu tutorial as default 22538
        self.__beatmap = TUTORIAL
        self.__beatmap_name = "osu! Tutorial"
        self.__match_history = self.fetch_match_history()
        self.__size = 16
        self.__locked = False
        self._password = ""
        self.__title = ""
        self.__welcome_message = ""
        self.__referees = [bot.get_username()]
        self.__config_link = ""
        self.__config_text = ""
        self.__custom_config_text = ""
        self.__beatmap_checker = False
        self.__start_timer = False
        self.__start_on_players_ready = False
        self.__autostart_timer = -1
        self.__maintain_password = False
        self.__maintain_size = False
        self.__maintain_title = False
        self.__player_blacklist = bot.get_player_blacklist().copy()
        self.__auto_download = {"status": False, "path": "", "auto_open": False, "with_video": False}
        self._commands = {"!info": {"response": "Built with [https://github.com/jramseygreen/osu_bot_framework-v3 osu_bot_framework v3] | [https://osu.ppy.sh/u/qqzzy Developer]", "description": "Built with osu_bot_framework v3"}}

        # limits and ranges (done)
        self.__ar_range = (0.0, 10.0)
        self.__od_range = (0.0, 10.0)
        self.__cs_range = (0.0, 10.0)
        self.__hp_range = (0.0, 10.0)
        self.__diff_range = (0.0, -1.0)
        self.__bpm_range = (0.0, -1.0)
        self.__length_range = (0, -1)
        self.__map_status = ["any"]
        self.__allow_unsubmitted = True

        # game attributes
        self.__mods = ["ANY"]
        self.__scoring_type = "any"
        self.__team_type = "any"
        self.__game_mode = "any"
        self.__allow_convert = True

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
        self.__on_rule_violation_method = None

        # whitelists + blacklists
        self.__beatmap_creator_whitelist = []
        self.__beatmap_creator_blacklist = []
        self.__artist_whitelist = []
        self.__artist_blacklist = []

    def process_message(self, message):
        super().process_message(message)
        # update room attributes
        if message["username"] == "BanchoBot":
            if "joined in slot" in message["content"]:
                username = message["content"][:message["content"].find("joined") - 1]
                team = ""
                if "for team" in message["content"]:
                    if "for team blue" in message["content"]:
                        team = "blue"
                    elif "for team red" in message["content"]:
                        team = "red"
                    if self.__on_team_addition_method:
                        argnum = len(str(inspect.signature(self.__on_team_addition_method)).strip("()").split(", "))
                        x = None
                        if argnum == 2:
                            x = threading.Thread(target=self.__on_team_addition_method, args=(username, team,))
                        elif str(inspect.signature(self.__on_team_addition_method)).strip("()").split(", ") != [""]:
                            x = threading.Thread(target=self.__on_team_addition_method, args=(username,))
                        else:
                            x = threading.Thread(target=self.__on_team_addition_method)
                        x.setDaemon(True)
                        x.start()
                        self._bot.log("-- on team addition method executed --")
                else:
                    self.clear_teams()
                slot_num = int(message["content"].split("slot ", 1)[1].split(".", 1)[0].split(" ")[0]) - 1
                self.set_slot(slot_num, {"username": username, "team": team, "score": {}})
                self.add_user(username)
                if self.has_referee(username):
                    self.add_referee(username)
            elif "left the game" in message["content"]:
                username = message["content"][:message["content"].find("left") - 1]
                self.del_user(username)
            elif "moved to slot" in message["content"]:
                slot = int(message["content"].split(" ")[-1]) - 1
                username = message["content"].replace(" moved to slot " + str(slot + 1), "")
                team = self.get_team(username)
                score = self.get_score(username)
                self.del_slot(self.get_slot_num(username))
                self.set_slot(slot, {"username": username, "team": team, "score": score})
                if self.__on_slot_change_method:
                    argnum = len(str(inspect.signature(self.__on_slot_change_method)).strip("()").split(", "))
                    x = None
                    if argnum == 2:
                        x = threading.Thread(target=self.__on_slot_change_method, args=(username, slot,))
                    elif str(inspect.signature(self.__on_slot_change_method)).strip("()").split(", ") != [""]:
                        x = threading.Thread(target=self.__on_slot_change_method, args=(username,))
                    else:
                        x = threading.Thread(target=self.__on_slot_change_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on slot change method executed --")

            elif "changed to Blue" in message["content"]:
                username = message["content"].replace(" changed to Blue", "")
                slot = self.get_slot_num(username)
                score = self.get_score(username)
                self.set_slot(slot, {"username": username, "team": "blue", "score": score})
                if self.__on_team_change_method:
                    argnum = len(str(inspect.signature(self.__on_team_change_method)).strip("()").split(", "))
                    x = None
                    if argnum == 2:
                        x = threading.Thread(target=self.__on_team_change_method, args=(username, "blue",))
                    elif str(inspect.signature(self.__on_team_change_method)).strip("()").split(", ") != [""]:
                        x = threading.Thread(target=self.__on_team_change_method, args=(username,))
                    else:
                        x = threading.Thread(target=self.__on_team_change_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on team change method executed --")

            elif "changed to Red" in message["content"]:
                username = message["content"].replace(" changed to Red", "")
                slot = self.get_slot_num(username)
                score = self.get_score(username)
                self.set_slot(slot, {"username": username, "team": "red", "score": score})
                if self.__on_team_change_method:
                    argnum = len(str(inspect.signature(self.__on_team_change_method)).strip("()").split(", "))
                    x = None
                    if argnum == 2:
                        x = threading.Thread(target=self.__on_team_change_method, args=(username, "red",))
                    elif str(inspect.signature(self.__on_team_change_method)).strip("()").split(", ") != [""]:
                        x = threading.Thread(target=self.__on_team_change_method, args=(username,))
                    else:
                        x = threading.Thread(target=self.__on_team_change_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on team change method executed --")
            elif "became the host" in message["content"]:
                self.__set_host(message["content"].replace(" became the host.", ""))
            elif "The match has started!" == message["content"]:
                self.abort_start_timer()
                self.__check_attributes()
            elif "The match has finished!" == message["content"]:
                self.__in_progress = False
                self.__fetch_scores()
                self.__maintain_attributes()
                if self.__on_match_finish_method:
                    x = threading.Thread(target=self.__on_match_finish_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on match finish method executed --")
            elif "Aborted the match" == message["content"]:
                self.__in_progress = False
            elif "Beatmap changed to" in message["content"] or "Changed beatmap to" in message["content"]:
                beatmapID = message["content"].split("/b/", 1)[1].split(" ", 1)[0].replace(")", "")
                self.__check_beatmap_attributes(beatmapID)
                line = message["content"].replace("Beatmap changed to:", "").replace("Changed beatmap to" ,"").split(" ")
                for item in line:
                    if "https://" in item:
                        line.remove(item)

                self.__beatmap_name = " ".join(line)
            elif "Host is changing map..." == message["content"]:
                self.abort_start_timer()
                if self.__on_changing_beatmap_method:
                    x = threading.Thread(target=self.__on_changing_beatmap_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on changing beatmap method executed --")
            elif "All players are ready" == message["content"]:
                if self.__on_all_players_ready_method:
                    x = threading.Thread(target=self.__on_all_players_ready_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on all players ready method executed --")
                if self.__start_on_players_ready:
                    self.start_match()
            elif "Cleared match host" == message["content"]:
                if self.__on_clear_host_method:
                    x = None
                    if str(inspect.signature(self.__on_clear_host_method)).strip("()").split(", ") != [""]:
                        x = threading.Thread(target=self.__on_clear_host_method, args=(self.__host,))
                    else:
                        x = threading.Thread(target=self.__on_clear_host_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on clear host method executed --")
                self.__host = ""
            elif "Room name updated to " in message["content"]:
                title = message["content"].replace("Room name updated to ", "").strip('"')
                if not title:
                    self.__title = self.__match_history["match"]["name"]
                else:
                    self.__title = title
            elif "Locked the match" == message["content"]:
                self.__locked = True
            elif "Unlocked the match" == message["content"]:
                self.__locked = False
            elif "Room name:" in message["content"]:
                self.__title = message["content"].replace("Room name: ", "").split(",", 1)[0]
            elif "osu.ppy.sh/u/" in message["content"]:
                slot = int(message["content"].split(" ", 2)[1]) - 1
                username = ""
                host = False
                team = ""
                for user in self._users:
                    if user in message["content"]:
                        username = user
                        break
                attr = message["content"].split(username, 1)
                if "Host" in attr[1]:
                    host = True
                if "Team Blue" in attr[1]:
                    team = "blue"
                elif "Team Red" in attr[1]:
                    team = "red"
                self.set_slot(slot, {"username": username, "team": team, "score": {}})
                if host:
                    self.__host = username

            elif "Beatmap:" in message["content"] and self.__beatmap == TUTORIAL:
                self.change_beatmap(message["content"].replace("Beatmap: ", "").split(" ", 1)[0].replace("https://osu.ppy.sh/b/", "", 1))
            elif "Changed match to size " in message["content"]:
                args = message["content"].split()
                self.__size = int(args[-1])

        elif self.has_referee(message["username"]):
            message_arr = message["content"].lower().split(" ")
            if len(message_arr) >= 2:
                command = " ".join(message_arr[:2]).strip()
                args = message_arr[2:]
                if message["username"] == self.__creator.replace(" ", "_"):
                    if command == "!mp addref":
                        for arg in args:
                            if arg not in self.__referees:
                                self.add_referee(arg)
                    elif command == "!mp removeref":
                        for username in args:
                            if username != self.__creator.replace(" ", "_") and username in self.__referees:
                                self.del_referee(username)
                                if username == self._bot.get_username():
                                    self._bot.part(self._channel)
                    self.get_config_link()
                if command == "!mp password":
                    self.__invite_link = self.__invite_link.replace(self._password, "")
                    if args:
                        self._password = args[0]
                        self.__invite_link = self.__invite_link + args[0]
                    else:
                        self._password = ""
                elif command == "!mp size":
                    if args:
                        self.__size = int(args[0])
                elif command == "!mp abort" and self.in_progress():
                    if self.__on_match_abort_method:
                        x = threading.Thread(target=self.__on_match_abort_method)
                        x.setDaemon(True)
                        x.start()
                        self._bot.log("-- on match abort method executed --")

        self.__execute_commands(message)

    def __execute_commands(self, message):
        for command in self._commands:
            if not message["content"].replace(command, "") or message["content"].replace(command, "")[0] == " ":
                if callable(self._commands[command]["response"]):
                    x = None
                    if str(inspect.signature(self._commands[command]["response"])).strip("()").split(", ") != [""]:
                        x = threading.Thread(target=self._commands[command]["response"], args=(message,))
                    else:
                        x = threading.Thread(target=self._commands[command]["response"])
                    x.setDaemon(True)
                    x.start()
                else:
                    self.send_message(str(self._commands[command]["response"]))
                self._bot.log("-- Command '" + command + "' Executed --")

    def send_message(self, message):
        super().send_message(message)
        self.__execute_commands({"username": self._bot.get_username(), "channel": self._channel, "content": message})

    def del_user(self, username):
        # remove from slots
        if self.has_user(username):
            for slot in self.__slots:
                if self.__slots[slot]["username"].replace(" ", "_") == username.replace(" ", "_"):
                    self.__slots[slot] = {"username": "", "team": "", "score": {}}
                    break
            super().del_user(username)
            if not self.has_users():
                self.abort_start_timer()
                self.__maintain_attributes()

    def add_user(self, username):
        super().add_user(username)
        # welcome message implementation
        if self.__welcome_message:
            self._bot.send_personal_message(username.replace(" ", "_"), self.__welcome_message)
        self.__kick_users()

    def __kick_users(self):
        for username in self.get_formatted_player_blacklist():
            if username in self._users:
                self.kick_user(username)
                self._bot.send_personal_message(username, "Sorry, you have been blacklisted from [https://osu.ppy.sh/mp/" + self._channel[4:] + " " + self.__title + "]")

    def kick_user(self, username):
        if username.replace(" ", "_") in self.get_formatted_users():
            self.send_message("!mp kick " + username.replace(" ", "_"))

    def get_formatted_users(self):
        return [user.replace(" ", "_") for user in self._users]

    def close(self):
        self.send_message("!mp close")
        self._bot.part(self._channel)

    def fetch_match_history(self):
        url = "https://osu.ppy.sh/community/matches/" + self._channel[4:]

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"

        r = requests.get(url, headers=headers)
        self._bot.log("-- Fetched match history --")
        return json.loads(r.text)

    def get_match_history(self):
        return self.__match_history

    # fetches the most recent match data from ppy.sh
    def get_match_data(self):
        for event in reversed(self.get_match_history()["events"]):
            if "game" in event:
                return event["game"]
        return {}

    # fetches beatmap from ppy.sh
    def __fetch_beatmap(self, beatmapID):
        if self.__beatmap:
            if int(beatmapID) == self.__beatmap["id"]:
                return self.__beatmap
        if int(beatmapID) == 0:
            return {}
        return self._bot.fetch_beatmap(beatmapID)

    # fetches a beatmapset associated with a beatmapID from ppy.sh
    def __fetch_beatmapset(self, beatmapID):
        if int(beatmapID) == 0:
            return {}
        return self._bot.fetch_beatmapset(beatmapID)

    def __fetch_scores(self):
        self.clear_scores()
        self.__match_history = self.fetch_match_history()
        for score in self.get_match_data()["scores"]:
            if self.__slots[score["match"]["slot"]]["username"]:
                self.__slots[score["match"]["slot"]]["score"] = score
                if not self.__slots[score["match"]["slot"]]["team"]:
                    self.__slots[score["match"]["slot"]]["team"] = score["match"]["team"]

    def clear_scores(self):
        for slot in self.__slots:
            self.__slots[slot]["score"] = {}

    def get_score(self, username):
        slot = self.get_slot(username)
        if slot:
            return slot["score"]

    def get_scores(self):
        scores = []
        for slot in self.__slots:
            if self.__slots[slot]["score"]:
                if "username" not in self.__slots[slot]["score"]:
                    self.__slots[slot]["score"]["username"] = self.__slots[slot]["username"]
                scores.append(self.__slots[slot]["score"])
        return scores

    def get_red_scores(self):
        scores = []
        for score in self.get_scores():
            if score["team"] == "red":
                scores.append(score)
        return scores

    def get_blue_scores(self):
        scores = []
        for score in self.get_scores():
            if score["team"] == "blue":
                scores.append(score)
        return scores

    def get_ordered_scores(self):
        passed = []
        failed = []
        for score in self.get_scores():
            if score["passed"]:
                passed.append(score)
            else:
                failed.append(score)
        match = self.get_match_data()
        key = "max_combo"
        if "score" in match["scoring_type"]:
            key = "score"
        elif "accuracy" == match["scoring_type"]:
            key = "accuracy"

        return sorted(passed, key=lambda x: x[key], reverse=True) + sorted(failed, key=lambda x: x[key], reverse=True)

    def has_score(self, username):
        if self.get_score(username):
            return True
        return False

    def __check_beatmap_attributes(self, beatmapID, running=False):
        if not running:
            x = threading.Thread(target=self.__check_beatmap_attributes, args=(beatmapID, True,))
            x.setDaemon(True)
            x.start()
        else:
            self._bot.log("-- Beatmap checker started --")
            beatmapID = int(beatmapID)
            accept_beatmap = False
            beatmap = None
            if beatmapID == self.__beatmap["id"]:
                beatmap = self.__beatmap
                accept_beatmap = True
            elif beatmapID == TUTORIAL["id"]:
                beatmap = TUTORIAL
                accept_beatmap = True
            else:
                beatmap = self.__fetch_beatmap(beatmapID)
                if self.__beatmap_checker:
                    if self.__allow_unsubmitted and not beatmap:
                        beatmap = {"id": beatmapID, "url": "https://osu.ppy.sh/b/" + str(beatmapID)}
                        accept_beatmap = True
                        self.send_message("Can't check attributes, the selected beatmap is unsubmitted! " + "[" + str(self._bot.chimu.fetch_download_link(beatmapID, False)) + " BeatConnect.io download]")
                    else:
                        error = self.check_beatmap(beatmap)
                        if error:
                            self.abort_start_timer()
                            if beatmap:
                                self.send_message("Rule violation: " + error["type"] + " - " + error["message"].replace("selected beatmap","[" + beatmap["url"] + " selected beatmap]"))
                            else:
                                self.send_message("Rule violation: " + error["type"] + " - " + error["message"])
                            self.set_beatmap(self.__beatmap)
                            if self.__on_rule_violation_method:
                                x = None
                                if str(inspect.signature(self.__on_rule_violation_method)).strip("()").split(", ") != [""]:
                                    x = threading.Thread(target=self.__on_rule_violation_method, args=(error,))
                                else:
                                    x = threading.Thread(target=self.__on_rule_violation_method)
                                x.setDaemon(True)
                                x.start()
                                self._bot.log("-- on rule violation method executed --")
                        else:
                            accept_beatmap = True
                else:
                    if not beatmap:
                        beatmap = {"id": beatmapID, "url": "https://osu.ppy.sh/b/" + str(beatmapID)}
                        self.send_message("The selected beatmap is unsubmitted! " + "[" + str(self._bot.chimu.fetch_download_link(beatmapID, False)) + " BeatConnect.io download]")
                    accept_beatmap = True

            if accept_beatmap:
                old_beatmap = self.__beatmap
                self.__beatmap = beatmap
                if self.__on_beatmap_change_method:
                    argnum = len(str(inspect.signature(self.__on_beatmap_change_method)).strip("()").split(", "))
                    x = None
                    if argnum == 2:
                        x = threading.Thread(target=self.__on_beatmap_change_method, args=(old_beatmap, beatmap,))
                    elif str(inspect.signature(self.__on_beatmap_change_method)).strip("()").split(", ") != [""]:
                        x = threading.Thread(target=self.__on_beatmap_change_method, args=(beatmap,))
                    else:
                        x = threading.Thread(target=self.__on_beatmap_change_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on beatmap change method executed --")

                if old_beatmap != beatmap:
                    if self.__auto_download["status"]:
                        self._bot.chimu.download_beatmap(beatmap["id"], path=self.__auto_download["path"], with_video=self.__auto_download["with_video"], auto_open=self.__auto_download["auto_open"])
                    if self.__autostart_timer > 0:
                        self.start_match(self.__autostart_timer)
            self._bot.log("-- Beatmap checker finished --")

    def __check_attributes(self, running=False):
        if not running:
            x = threading.Thread(target=self.__check_attributes, args=(True,))
            x.setDaemon(True)
            x.start()
        else:
            self._bot.log("-- Attribute checker started --")
            self.__match_history = self.fetch_match_history()
            match = self.get_match_data()
            abort = False
            error = ""

            if not match:
                abort = True
                error = {"type": "match_history", "message": "The match history cannot be read! Check that the match history is public."}
            elif self.__scoring_type.lower() != "any" and match["scoring_type"] != self.__scoring_type.lower():
                error = {"type": "scoring", "message": "The allowed scoring type is: " + self.__scoring_type}
                abort = True
            elif self.__mods != ["ANY"]:
                if "FREEMOD" in self.__mods and match["mods"] != []:
                    error = {"type": "mods", "message": "The allowed mods are: " + ", ".join(self.__mods)}
                    abort = True
                elif self.__mods != ["FREEMOD"] and (not all([mod in self.__mods for mod in match["mods"]]) or not all([mod in match["mods"] for mod in self.__mods])):
                    error = {"type": "mods", "message": "The allowed mods are: " + ", ".join(self.__mods)}
                    abort = True
            elif self.__team_type != "any" and self.__team_type.lower() != match["team_type"]:
                error = {"type": "team", "message": "The allowed team type is: " + self.__team_type}
                abort = True
            elif self.__beatmap_checker and self.__game_mode.lower() != "any" and match["mode"] != self.__game_mode.lower():
                error = {"type": "mode", "message": "The selected beatmap's mode must be: " + self.__game_mode}
                abort = True
            elif "beatmap" in match and self.__beatmap["id"] != match["beatmap"]["id"]:
                abort = True
            elif self.__beatmap_checker:
                error = self.check_beatmap(self.__beatmap)
                if error and error["type"] == "unsubmitted":
                    if not self.__allow_unsubmitted:
                        abort = True
                elif error:
                    abort = True

            if abort:
                # execute on_rule_break
                self.send_message("!mp abort")
                self.send_message("!mp set " + str(GAME_ATTR[self.__team_type]) + " " + str(GAME_ATTR[self.__scoring_type]) + " " + str(self.__size))
                game_mode = ""
                if self.__game_mode != "any":
                    game_mode = str(GAME_ATTR[self.__game_mode])
                self.send_message("!mp map " + str(self.__beatmap["id"]) + " " + game_mode)
                self.set_mods(self.__mods)
                self.send_message("Rule violation: " + error["type"] + " - " + error["message"].replace("selected beatmap", "[" + self.__beatmap["url"] + " selected beatmap]"))
                if self.__on_rule_violation_method:
                    x = None
                    if str(inspect.signature(self.__on_rule_violation_method)).strip("()").split(", ") != [""]:
                        x = threading.Thread(target=self.__on_rule_violation_method, args=(error,))
                    else:
                        x = threading.Thread(target=self.__on_rule_violation_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on rule violation method executed --")
            else:
                self.__in_progress = True
                if self.__on_match_start_method:
                    x = threading.Thread(target=self.__on_match_start_method)
                    x.setDaemon(True)
                    x.start()
                    self._bot.log("-- on match start method executed --")
                if "team" not in match["team_type"]:
                    self.clear_teams()
            self._bot.log("-- Attribute checker finished --")

    def check_beatmap(self, beatmap):
        error = ""
        if not beatmap or len(beatmap) == 2:
            error = {"type": "unsubmitted", "message": "Only submitted beatmaps are allowed"}
        elif self.__od_range[0] > beatmap["accuracy"] or beatmap["accuracy"] > self.__od_range[1]:
            error = {"type": "od", "message": "The selected beatmap is outside the overall difficulty range: " + str(self.__od_range)}
        elif self.__ar_range[0] > beatmap["ar"] or beatmap["ar"] > self.__ar_range[1]:
            error = {"type": "ar", "message": "The selected beatmap is outside the approach rate range: " + str(self.__ar_range)}
        elif self.__bpm_range[0] > beatmap["bpm"] or (self.__bpm_range[1] != -1 and self.__bpm_range[1] < beatmap["bpm"]):
            error = {"type": "bpm", "message": "The selected beatmap is outside the BPM range: " + str(self.__bpm_range).replace("-1.0", "unlimited")}
        elif self.__cs_range[0] > beatmap["cs"] or beatmap["cs"] > self.__cs_range[1]:
            error = {"type": "cs", "message": "The selected beatmap is outside the circle size range: " + str(self.__cs_range)}
        elif self.__hp_range[0] > beatmap["drain"] or beatmap["drain"] > self.__hp_range[1]:
            error = {"type": "hp", "message": "The selected beatmap is outside the HP range: " + str(self.__hp_range)}
        elif self.__length_range[0] > beatmap["total_length"] or (self.__length_range[1] != -1 and self.__length_range[1] < beatmap["hit_length"]):
            if self.__length_range[1] == -1:
                error = {"type": "length", "message": "The selected beatmap is outside the length range: " + str([str(x // 60) + "min, " + str(x % 60) + "sec" for x in [self.__length_range[0]]] + ["unlimited"])}
            else:
                error = {"type": "length", "message": "The selected beatmap is outside the length range: " + str([str(x // 60) + "min, " + str(x % 60) + "sec" for x in self.__length_range])}
        elif self.__map_status != ["any"] and beatmap["status"] not in self.__map_status:
            error = {"type": "status", "message": "The selected beatmap must be: " + " or ".join(self.__map_status)}
        elif beatmap["difficulty_rating"] < self.__diff_range[0] or (beatmap["difficulty_rating"] > self.__diff_range[1] != -1):
            error = {"type": "difficulty", "message": "The selected beatmap is outside the difficulty range: " + str(self.__diff_range).replace("-1.0", "unlimited") + "*"}
        elif self.__game_mode != "any" and beatmap["mode"] != self.__game_mode and not self.__allow_convert:
            error = {"type": "mode", "message": "The selected beatmap's mode must be: " + self.__game_mode}
        elif self.__beatmap_creator_blacklist or self.__beatmap_creator_whitelist or self.__artist_blacklist or self.__artist_whitelist:
            beatmapset = self.__fetch_beatmapset(beatmap["id"])
            if self.__beatmap_creator_whitelist and beatmapset["creator"].lower() not in self.__beatmap_creator_whitelist and all([x not in beatmap["version"].lower() for x in self.__beatmap_creator_whitelist]):
                error = {"type": "creator_whitelist", "message": "The beatmap creator is not whitelisted. The whitelist is: '" + "', '".join(self.__beatmap_creator_whitelist) + "'"}
            elif self.__beatmap_creator_blacklist and beatmapset["creator"].lower() in self.__beatmap_creator_blacklist or any([x in beatmap["version"].lower() for x in self.__beatmap_creator_blacklist]):
                error = {"type": "creator_blacklist", "message": "The beatmap creator is blacklisted. The blacklist is: '" + "', '".join(self.__beatmap_creator_blacklist) + "'"}
            elif self.__artist_whitelist and beatmapset["artist"].lower() not in self.__artist_whitelist:
                error = {"type": "artist_whitelist", "message": "The beatmap artist is not whitelisted. The whitelist is: '" + "', '".join(self.__artist_whitelist) + "'"}
            elif self.__artist_blacklist and beatmapset["artist"].lower() in self.__artist_blacklist:
                error = {"type": "artist_blacklist", "message": "The beatmap artist is blacklisted. The blacklist is: '" + "', '".join(self.__artist_blacklist) + "'"}
        return error

    def abort_match(self):
        self.send_message("!mp abort")
        self.__maintain_attributes()
        if self.__on_match_abort_method:
            x = threading.Thread(target=self.__on_match_abort_method)
            x.setDaemon(True)
            x.start()
            self._bot.log("-- on match abort method executed --")

    def __maintain_attributes(self):
        if self.__maintain_size:
            self.set_size(self.__size)
        if self.__maintain_password:
            self.set_password(self._password)
        if self.__maintain_title:
            self.set_title(self.__title)

    def start_match(self, secs=0, running=False):
        if not running:
            x = threading.Thread(target=self.start_match, args=(secs, True,))
            x.setDaemon(True)
            x.start()
        else:
            self.__start_timer = False
            secs = int(secs)
            if secs > 0:
                time.sleep(1.1)
                self.__start_timer = True
                if self.has_users():
                    msg = ("Queued the match to start in " + str(secs // 60) + " minutes " + str(secs % 60) + " seconds").replace(" 0 minutes", "").replace(" 0 seconds", "").replace("1 minutes", "1 minute")
                    for command in self._commands:
                        if self._commands[command]["response"] == self.common_commands.abort_start_timer:
                            msg += " (" + command + " to stop)"
                            break
                    self.send_message(msg)
                secs -= 1
                while secs > 0:
                    time.sleep(1)
                    if not self.__start_timer or not self._bot.has_channel(self._channel) or not self.has_users() or self.in_progress():
                        return
                    if secs % 30 == 0 or secs == 10 or secs <= 5:
                        self.send_message(("Match starts in " + str(secs // 60) + " minutes " + str(secs % 60) + " seconds").replace(" 0 minutes", "").replace(" 0 seconds", "").replace("1 minutes", "1 minute"))
                    if secs == 1:
                        self.send_message("Good luck & Have fun!")
                    secs -= 1

            self.send_message("!mp start")
            self.__start_timer = False

    def abort_start_timer(self):
        self.__start_timer = False

    def in_progress(self):
        return self.__in_progress

    def set_invite_link(self, link):
        self.__invite_link = link

    def get_invite_link(self):
        return self.__invite_link

    def get_slots(self):
        return self.__slots

    def get_formatted_slots(self):
        slots = {}
        for slot in self.__slots:
            slots[slot] = {"username": self.__slots[slot]["username"].replace(" ", "_"), "team": self.__slots[slot]["team"], "score": self.__slots[slot]["score"]}
        return slots

    def set_slot(self, slot, data):
        if type(slot) == int:
            self.__slots[slot] = data

    def del_slot(self, slot):
        if type(slot) == int:
            self.__slots[slot] = {"username": "", "team": "", "score": {}}

    def get_slot(self, username):
        slotnum = self.get_slot_num(username)
        if slotnum:
            return self.__slots[slotnum]

    def get_formatted_slot(self, username):
        slotnum = self.get_slot_num(username)
        if slotnum:
            return self.get_formatted_slots()[slotnum]

    def get_slot_username(self, number):
        return self.__slots[number]["username"]

    def get_formatted_slot_username(self, number):
        return self.get_formatted_slots()[number]["username"]

    def get_slot_num(self, username):
        for i in range(16):
            if self.__slots[i]["username"].replace(" ", "_") == username.replace(" ", "_"):
                return i

    def get_next_empty_slot_num(self, offset=0):
        for i in range(offset, 16):
            if not self.__slots[i]["username"]:
                return i
        for i in range(0, offset):
            if not self.__slots[i]["username"]:
                return i

    def get_next_full_slot_num(self, offset=0):
        for i in range(offset, 16):
            if self.__slots[i]["username"]:
                return i
        for i in range(0, offset):
            if self.__slots[i]["username"]:
                return i

    def clear_teams(self):
        for slot in self.__slots:
            self.__slots[slot]["team"] = ""

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

    def get_formatted_host(self):
        return self.__host.replace(" ", "_")

    def is_host(self, username):
        return username.replace(" ", "_") == self.get_formatted_host()

    def __set_host(self, username):
        old_host = self.__host
        self.__host = username
        if self.__on_host_change_method:
            argnum = len(str(inspect.signature(self.__on_host_change_method)).strip("()").split(", "))
            x = None
            if argnum == 2:
                x = threading.Thread(target=self.__on_host_change_method, args=(old_host, username,))
            elif str(inspect.signature(self.__on_host_change_method)).strip("()").split(", ") != [""]:
                x = threading.Thread(target=self.__on_host_change_method, args=(username,))
            else:
                x = threading.Thread(target=self.__on_host_change_method)
            x.setDaemon(True)
            x.start()
            self._bot.log("-- on host change method executed --")

    def set_host(self, username):
        self.__host = username
        self.send_message("!mp host " + username.replace(" ", "_"))

    def set_password(self, password):
        password = password.strip()
        if password != self._password:
            self.__invite_link = self.__invite_link.replace(self._password.replace(" ", "_"), "")
            self._password = password
            self.__invite_link = self.__invite_link + password.replace(" ", "_")
        self.send_message("!mp password " + self._password)

    def get_password(self):
        return self._password

    def has_password(self):
        return self._password != ""

    def add_referee(self, username):
        if username not in self.__referees:
            self.__referees.append(username)

    def del_referee(self, username):
        if username in self.__referees:
            self.__referees.remove(username)

    def get_referees(self):
        return self.__referees

    def get_formatted_referees(self):
        return [ref.replace(" ", "_") for ref in self.__referees]

    def has_referee(self, username):
        return username.replace(" ", "_").lower() in [x.lower() for x in self.get_formatted_referees()]

    def get_creator(self):
        return self.__creator

    def is_creator(self, username):
        return username.replace(" ", "_") == self.__creator.replace(" ", "_")

    def get_formatted_creator(self):
        return self.__creator.replace(" ", "_")

    # grabs existing users, the room creator, and adds creator to referee list
    def get_existing_attributes(self):
        for user in self.__match_history["users"]:
            if self.has_user(user["username"].replace(" ", "_")):
                self._users.remove(user["username"].replace(" ", "_"))
                self.add_user(user["username"])

        self.__creator = self._bot.fetch_user_profile(self.__match_history["events"][0]["user_id"])["username"]
        self.add_referee(self.__creator)
        self.send_message("!mp settings")

    def set_beatmap(self, beatmap):
        if beatmap:
            self.__beatmap = beatmap
            self.change_beatmap(beatmap["id"])

    def get_beatmap(self):
        return self.__beatmap

    def change_beatmap(self, beatmapID):
        game_mode = ""
        if self.__game_mode != "any":
            game_mode = str(GAME_ATTR[self.__game_mode])
        self.send_message("!mp map " + str(beatmapID) + " " + game_mode)

    # getters and setters for limits and ranges
    # sets the allowed map statuses
    def set_map_status(self, status):
        if not status:
            status = ["any"]
        if type(status) == list:
            self.__map_status = [x.lower() for x in status]
        else:
            self.__map_status = [status.lower()]

    # returns the allowed map statuses
    def get_map_status(self):
        return self.__map_status

    # sets the allowed difficulty range
    def set_diff_range(self, range):
        if range[0] == "":
            range[0] = self.__diff_range[0]
        if range[1] == "":
            range[1] = self.__diff_range[1]
        self.__diff_range = (float(range[0]), float(range[1]))

    # returns the allowed difficulty range
    def get_diff_range(self):
        return self.__diff_range

    # sets the allowed mods
    def set_mods(self, mods):
        if not mods:
            mods = ["any"]
        if type(mods) == list:
            mods = [mod.upper() for mod in mods]
        else:
            mods = [mods.upper()]
        self.__mods = mods
        if self.__mods != ["ANY"]:
            msg = " ".join([GAME_ATTR[x] for x in self.__mods]).lower()
            if "EZ" in self.__mods and "HR" in self.__mods:
                msg = (msg.replace("hr", "18").replace("ez", "18")).strip()

            self.send_message("!mp mods " + msg)

    # gets the allowed mods
    def get_mods(self):
        return self.__mods

    # sets the allowed approach rate range
    def set_ar_range(self, range):
        if range[0] == "":
            range[0] = self.__ar_range[0]
        if range[1] == "":
            range[1] = self.__ar_range[1]
        self.__ar_range = (float(range[0]), float(range[1]))

    # returns the allowed approach rate range
    def get_ar_range(self):
        return self.__ar_range

    # sets the allowed overall difficulty range
    def set_od_range(self, range):
        if range[0] == "":
            range[0] = self.__od_range[0]
        if range[1] == "":
            range[1] = self.__od_range[1]
        self.__od_range = (float(range[0]), float(range[1]))

    # gets the allowed overall difficulty range
    def get_od_range(self):
        return self.__od_range

    # sets the allowed circle size range
    def set_cs_range(self, range):
        if range[0] == "":
            range[0] = self.__cs_range[0]
        if range[1] == "":
            range[1] = self.__cs_range[1]
        self.__cs_range = (float(range[0]), float(range[1]))

    # gets the allowed circle size range
    def get_cs_range(self):
        return self.__cs_range

    # sets the allowed hp range
    def set_hp_range(self, range):
        if range[0] == "":
            range[0] = self.__hp_range[0]
        if range[1] == "":
            range[1] = self.__hp_range[1]
        self.__hp_range = (float(range[0]), float(range[1]))

    # gets the allowed hp range
    def get_hp_range(self):
        return self.__hp_range

    # sets the allowed bpm range
    def set_bpm_range(self, range):
        if range[0] == "":
            range[0] = self.__bpm_range[0]
        if range[1] == "":
            range[1] = self.__bpm_range[1]
        self.__bpm_range = (float(range[0]), float(range[1]))

    # returns the allowed bpm range
    def get_bpm_range(self):
        return self.__bpm_range

    # sets the allowed beatmap length range
    def set_length_range(self, range):
        if range[0] == "":
            range[0] = self.__length_range[0]
        if range[1] == "":
            range[1] = self.__length_range[1]
        self.__length_range = (int(range[0]), int(range[1]))

    # returns the allowed beatmap length range
    def get_length_range(self):
        return self.__length_range

    # sets the allowed room scoring types
    def set_scoring_type(self, scoring_type):
        self.__scoring_type = scoring_type.lower()
        if scoring_type != "any":
            self.send_message("!mp set scoremode " + str(GAME_ATTR[self.__scoring_type]))

    # returns the scoring type of the room
    def get_scoring_type(self):
        return self.__scoring_type

    # sets the team type of the room
    def set_team_type(self, team_type):
        old = self.__team_type
        self.__team_type = team_type.lower().replace(" ", "-").replace("co-op", "coop")
        if self.__team_type != "any":
            self.send_message("!mp set " + str(GAME_ATTR[self.__team_type]))
            if "team" in self.__team_type and "team" not in old:
                for user in self._users:
                    if self._users.index(user) % 2 == 0:
                        self.__slots[self.get_slot_num(user)]["team"] = "blue"
                    else:
                        self.__slots[self.get_slot_num(user)]["team"] = "red"
            else:
                self.clear_teams()

    # returns the tracked team type of the room
    def get_team_type(self):
        return self.__team_type

    # sets the tracked game mode
    def set_game_mode(self, mode):
        self.__game_mode = mode.lower()
        if self.__game_mode != "any":
            if self.__beatmap:
                self.send_message("!mp map " + str(self.__beatmap["id"]) + " " + str(GAME_ATTR[self.__game_mode]))
            else:
                self.send_message("!mp map 22538 " + str(GAME_ATTR[self.__game_mode]))

    # returns the game mode of the room
    def get_game_mode(self):
        return self.__game_mode

    def set_title(self, title):
        self.send_message("!mp name " + title)

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
        text = str(self.__custom_config_text) + "\n"
        text += "𝙶̲𝚊̲𝚖̲𝚎̲ ̲𝚁̲𝚘̲𝚘̲𝚖̲ ̲𝙲̲𝚘̲𝚗̲𝚏̲𝚒̲𝚐̲𝚞̲𝚛̲𝚊̲𝚝̲𝚒̲𝚘̲𝚗̲:"
        text += "\n     • Title: " + self.__title
        text += "\n     • Channel: " + self._channel
        text += "\n     • Logic profile: " + self._logic_profile
        text += "\n     • Match history: https://osu.ppy.sh/mp/" + self._channel.replace("#mp_", "", 1) + "/"
        text += "\n     • Invite link: " + self.__invite_link
        text += "\n     • Referees: " + ", ".join(self.__referees).replace(self.__creator, self.__creator + " (Room creator)")
        text += "\n     • Player blacklist: " + ", ".join(self.__player_blacklist)
        text += "\n     • Welcome message: " + self.__welcome_message
        text += "\n     • Beatmap checker: " + str(self.__beatmap_checker)
        text += "\n     • Maintain title: " + str(self.__maintain_title)
        text += "\n     • Maintain password: " + str(self.__maintain_password)
        text += "\n     • Maintain size: " + str(self.__maintain_size)
        text += "\n     • Start on players ready: " + str(self.__start_on_players_ready)
        text += "\n     • Autostart timer: " + str(self.is_autostart_timer()) + " " + str(self.__autostart_timer) + "secs"
        text += "\n\n 𝙶̲𝚊̲𝚖̲𝚎̲ ̲𝚛̲𝚘̲𝚘̲𝚖̲ ̲𝚊̲𝚝̲𝚝̲𝚛̲𝚒̲𝚋̲𝚞̲𝚝̲𝚎̲𝚜̲:"
        text += "\n     • Room size: " + str(self.__size)
        text += "\n     • Game mode: " + self.__game_mode
        text += "\n     • Scoring mode: " + self.__scoring_type
        text += "\n     • Team mode: " + self.__team_type
        text += "\n     • Allow beatmap conversion: " + str(self.__allow_convert)
        text += "\n     • Allow unsubmitted beatmaps: " + str(self.__allow_unsubmitted)
        text += "\n     • Mods: " + ", ".join(self.__mods)
        text += "\n     • Beatmap status: " + ", ".join(self.__map_status)
        text += "\n     • Artist whitelist: " + ", ".join(self.__artist_whitelist)
        text += "\n     • Artist blacklist: " + ", ".join(self.__artist_blacklist)
        text += "\n     • Beatmap creator whitelist: " + ", ".join(self.__beatmap_creator_whitelist)
        text += "\n     • Beatmap creator blacklist: " + ", ".join(self.__beatmap_creator_blacklist)
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
        for command in self._commands:
            text += "\n     • " + command + ": " + self._commands[command]["description"]

        text += "\n\n 𝚃̲𝚑̲𝚎̲ ̲𝚏̲𝚘̲𝚕̲𝚕̲𝚘̲𝚠̲𝚒̲𝚗̲𝚐̲ ̲𝚖̲𝚎̲𝚜̲𝚜̲𝚊̲𝚐̲𝚎̲𝚜̲ ̲𝚊̲𝚛̲𝚎̲ ̲𝚋̲𝚎̲𝚒̲𝚗̲𝚐̲ ̲𝚋̲𝚛̲𝚘̲𝚊̲𝚍̲𝚌̲𝚊̲𝚜̲𝚝̲ ̲𝚘̲𝚗̲ ̲𝚊̲ ̲𝚝̲𝚒̲𝚖̲𝚎̲𝚛̲:"
        text += "\n\n     𝙸̲𝙳̲   𝙼̲𝚎̲𝚜̲𝚜̲𝚊̲𝚐̲𝚎̲"
        broadcasts = self._bot.get_broadcast_controller().get_broadcasts(self._channel)
        for broadcast in broadcasts:
            if type(broadcasts) == list:
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

    def on_rule_violation(self, method):
        self.__on_rule_violation_method = method
        
    def implement_logic_profile(self, prof):
        profile = super().implement_logic_profile(prof)
        if profile or prof == "":
            self.abort_start_timer()
        if prof == "":
            self.send_message("Cleared current logic profile")
        if profile:
            if hasattr(profile, "on_match_start") and callable(getattr(profile, "on_match_start")):
                self.on_match_start(profile.on_match_start)
            if hasattr(profile, "on_match_finish") and callable(getattr(profile, "on_match_finish")):
                self.on_match_finish(profile.on_match_finish)
            if hasattr(profile, "on_match_abort") and callable(getattr(profile, "on_match_abort")):
                self.on_match_abort(profile.on_match_abort)
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
            if hasattr(profile, "on_rule_violation") and callable(getattr(profile, "on_rule_violation")):
                self.on_rule_violation(profile.on_rule_violation)
            self.send_message("Implemented logic profile: " + prof)

    def get_attributes(self):
        data = super().get_attributes()
        data["creator"] = self.__creator
        data["invite_link"] = self.__invite_link
        data["slots"] = self.__slots
        data["host"] = self.__host
        data["in_progress"] = self.__in_progress
        data["beatmap"] = self.__beatmap
        data["beatmap_name"] = self.__beatmap_name
        data["size"] = self.__size
        data["password"] = self._password
        data["title"] = self.__title
        data["welcome_message"] = self.__welcome_message
        data["referees"] = self.__referees
        data["config_link"] = self.__config_link
        data["beatmap_checker"] = self.__beatmap_checker
        data["creator_whitelist"] = self.__beatmap_creator_whitelist
        data["creator_blacklist"] = self.__beatmap_creator_blacklist
        data["artist_whitelist"] = self.__artist_whitelist
        data["artist_blacklist"] = self.__artist_blacklist
        data["player_blacklist"] = self.__player_blacklist
        data["autostart_timer"] = self.__autostart_timer
        data["maintain_title"] = self.__maintain_title
        data["maintain_password"] = self.__maintain_password
        data["maintain_size"] = self.__maintain_size
        data["beatmap_checker"] = self.__beatmap_checker
        data["start_on_players_ready"] = self.__start_on_players_ready
        data["auto_download"] = self.__auto_download

        # limits and ranges (done)
        data["ar_range"] = self.__ar_range
        data["od_range"] = self.__od_range
        data["cs_range"] = self.__cs_range
        data["hp_range"] = self.__hp_range
        data["diff_range"] = self.__diff_range
        data["bpm_range"] = self.__bpm_range
        data["length_range"] = self.__length_range
        data["map_status"] = self.__map_status
        data["allow_unsubmitted"] = self.__allow_unsubmitted

        # game attributes
        data["mods"] = self.__mods
        data["scoring_type"] = self.__scoring_type
        data["team_type"] = self.__team_type
        data["game_mode"] = self.__game_mode
        data["allow_convert"] = self.__allow_convert

        return data

    def clear_logic(self):
        super().clear_logic()
        self.on_match_start(None)
        self.on_match_finish(None)
        self.on_match_abort(None)
        self.on_host_change(None)
        self.on_beatmap_change(None)
        self.on_changing_beatmap(None)
        self.on_all_players_ready(None)
        self.on_room_close(None)
        self.on_slot_change(None)
        self.on_team_change(None)
        self.on_team_addition(None)
        self.on_clear_host(None)
        self.on_rule_violation(None)

    def get_logic(self):
        logic = super().get_logic()
        logic["on_match_start"] = self.__on_match_start_method
        logic["on_match_finish"] = self.__on_match_finish_method
        logic["on_match_abort"] = self.__on_match_abort_method
        logic["on_host_change"] = self.__on_host_change_method
        logic["on_beatmap_change"] = self.__on_beatmap_change_method
        logic["on_changing_beatmap"] = self.__on_changing_beatmap_method
        logic["on_all_players_ready"] = self.__on_all_players_ready_method
        logic["on_room_close"] = self.__on_room_close_method
        logic["on_slot_change"] = self.__on_slot_change_method
        logic["on_team_change"] = self.__on_team_change_method
        logic["on_team_addition_method"] = self.__on_team_addition_method
        logic["on_clear_host"] = self.__on_clear_host_method
        logic["on_rule_violation"] = self.__on_rule_violation_method
        return logic

    # overwrites certain room attributes
    def import_attributes(self, data):
        self.set_beatmap(data["beatmap"])
        self.set_size(data["size"])
        self.set_password(data["password"])
        self.set_welcome_message(data["welcome_message"])
        self.__autostart_timer = data["autostart_timer"]
        self.__maintain_title = data["maintain_title"]
        self.__maintain_password = data["maintain_password"]
        self.__maintain_size = data["maintain_size"]
        self.__beatmap_checker = data["beatmap_checker"]
        self.__start_on_players_ready = data["start_on_players_ready"]
        self.__player_blacklist = data["player_blacklist"]
        self.auto_download(data["auto_download"]["status"], data["auto_download"]["path"], data["auto_download"]["auto_open"], data["auto_download"]["with_video"])

        # limits and ranges (done)
        self.set_ar_range(data["ar_range"])
        self.set_od_range(data["od_range"])
        self.set_cs_range(data["cs_range"])
        self.set_hp_range(data["hp_range"])
        self.set_diff_range(data["diff_range"])
        self.set_bpm_range(data["bpm_range"])
        self.set_length_range(data["length_range"])
        self.set_map_status(data["map_status"])
        self.set_allow_unsubmitted(data["allow_unsubmitted"])

        # game attributes
        self.set_mods(data["mods"])
        self.set_scoring_type(data["scoring_type"])
        self.set_team_type(data["team_type"])
        self.set_game_mode(data["game_mode"])
        self.set_allow_convert(data["allow_convert"])
        self.set_allow_convert(data["allow_convert"])

    def invite_user(self, username):
        while not self.__title or not self.__invite_link:
            pass
        self._bot.send_personal_message(username.replace(" ", "_"), "Come join my multiplayer match: '[" + self.__invite_link + " " + self.__title + "]'")

    def set_beatmap_checker(self, switch):
        self.__beatmap_checker = switch

    def beatmap_checker_on(self):
        return self.__beatmap_checker

    def get_beatmap_creator_whitelist(self):
        return self.__beatmap_creator_whitelist

    def add_beatmap_creator_whitelist(self, creator):
        if creator and creator.lower() not in self.__beatmap_creator_whitelist:
            self.__beatmap_creator_whitelist.append(creator.lower())

    def del_beatmap_creator_whitelist(self, creator):
        if creator.lower() in self.__beatmap_creator_whitelist:
            self.__beatmap_creator_whitelist.remove(creator.lower())

    def get_beatmap_creator_blacklist(self):
        return self.__beatmap_creator_blacklist

    def add_beatmap_creator_blacklist(self, creator):
        if creator and creator.lower() not in self.__beatmap_creator_blacklist:
            self.__beatmap_creator_blacklist.append(creator.lower())

    def del_beatmap_creator_blacklist(self, creator):
        if creator.lower() in self.__beatmap_creator_blacklist:
            self.__beatmap_creator_blacklist.remove(creator.lower())

    def get_artist_whitelist(self):
        return self.__artist_whitelist

    def add_artist_whitelist(self, artist):
        if artist and artist.lower() not in self.__artist_whitelist:
            self.__artist_whitelist.append(artist.lower())

    def del_artist_whitelist(self, artist):
        if artist.lower() in self.__artist_whitelist:
            self.__artist_whitelist.remove(artist.lower())

    def get_artist_blacklist(self):
        return self.__artist_blacklist

    def add_artist_blacklist(self, artist):
        if artist and artist.lower() not in self.__artist_blacklist:
            self.__artist_blacklist.append(artist.lower())

    def del_artist_blacklist(self, artist):
        if artist.lower() in self.__artist_blacklist:
            self.__artist_blacklist.remove(artist.lower())

    def is_start_timer(self):
        return self.__start_timer

    def start_on_players_ready(self, status):
        self.__start_on_players_ready = status

    def is_start_on_players_ready(self):
        return self.__start_on_players_ready

    def set_autostart_timer(self, status, secs):
        if not status:
            secs = -1
        self.__autostart_timer = int(secs)
        if secs == -1:
            self.abort_start_timer()

    def get_autostart_timer(self):
        return self.__autostart_timer

    def is_autostart_timer(self):
        return self.__autostart_timer > -1

    def maintain_title(self, status):
        self.__maintain_title = status

    def maintain_password(self, status):
        self.__maintain_password = status

    def maintain_size(self, status):
        self.__maintain_size = status

    def is_maintain_title(self):
        return self.__maintain_title

    def is_maintain_size(self):
        return self.__maintain_size

    def is_maintain_password(self):
        return self.__maintain_password

    def get_player_blacklist(self):
        return self.__player_blacklist

    def get_formatted_player_blacklist(self):
        return [x.replace(" ", "_") for x in self.__player_blacklist]

    def set_player_blacklist(self, blacklist):
        self.__player_blacklist = blacklist
        self.__kick_users()

    def add_player_blacklist(self, username):
        if username.replace(" ", "_") not in self.get_formatted_player_blacklist():
            self.__player_blacklist.append(username)
        self.__kick_users()

    def del_player_blacklist(self, username):
        if username.replace(" ", "_") in self.get_formatted_player_blacklist():
            del self.__player_blacklist[self.get_formatted_player_blacklist().index(username.replace(" ", "_"))]

    def auto_download(self, status, path="", auto_open=False, with_video=False):
        self.__auto_download = {"status": status, "path": path, "auto_open": auto_open, "with_video": with_video}

    def set_allow_convert(self, status):
        self.__allow_convert = status

    def is_allow_convert(self):
        return self.__allow_convert

    def set_custom_config(self, text):
        self.__custom_config_text = text

    def get_custom_config(self):
        return self.__custom_config_text

    def clear_host(self):
        self.send_message("!mp clearhost")

    def set_allow_unsubmitted(self, status):
        self.__allow_unsubmitted = status

    def is_allow_unsubmitted(self):
        return self.__allow_unsubmitted

    def get_beatmap_name(self):
        return self.__beatmap_name

    def close_room(self):
        self.send_message("!mp close")

    def lock(self):
        self.send_message("!mp lock")
        self.__locked = True

    def unlock(self):
        self.send_message("!mp unlock")
        self.__locked = False

    def is_locked(self):
        return self.__locked
