import html
import importlib
import inspect
import json
import os
import pathlib
import sys
import threading
import time
from datetime import datetime

from tools.broadcast_controller import BroadcastController
from channel import Channel
from tools.chimu_wrapper import Chimu
from game import Game
from socket_wrapper import Sock
from tools.logger import Logger
from webapp.controller import Controller
import requests


class Bot:
    def __init__(self, username="", password="", host="irc.ppy.sh", port=6667, server_ip="localhost", message_log_length=50, logging=False, verbose=False):
        self.__sock = Sock()
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__controller = Controller(self, host=server_ip)
        self.__authenticate = False
        self.__started = False
        self.__channels = {}
        self.__default_message_log_length = message_log_length
        self.__personal_message_log = []
        self.__personal_message_log_length = self.__default_message_log_length
        self.__room_limit_reached = False
        self.__make_room_lock = threading.Lock()
        self.__new_tournament = ""
        self.__broadcast_controller = BroadcastController(self)
        self.__on_personal_message_method = None
        self.__logic_profiles = {}
        self.__logic_profile_links = {}
        self.__player_blacklist = []
        self.__osu_directory = ""
        self.chimu = Chimu(self)
        self.__logger = Logger("config" + os.sep + "logs" + os.sep + str(datetime.now()).replace(" ", "_", 1).replace(":", "-").split(".", 1)[0] + ".txt", "a", encoding="utf8")
        self.logging = logging
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)
        if self.logging:
            self.__logger.write("\n" + message)

    def __listen(self, running=False):
        if not running:
            threading.Thread(target=self.__listen, args=(True,)).start()
        else:
            self.__started = True
            buffer = ""
            # end condition
            while self.__started:
                # add to the buffer every loop
                data = self.__sock.get_socket().recv(2048)
                try:
                    buffer += data.decode("utf-8").replace("\r", "")
                except UnicodeDecodeError:
                    continue
                # while there are messages
                while "\n" in buffer:
                    msg = buffer.split("\n", 1)[0]
                    buffer = buffer.replace(msg + "\n", "", 1)

                    # ping pong
                    if msg[:4] == "PING":
                        self.__sock.sendall((msg.replace("PING", "PONG") + "\n").encode())
                        self.log("-- RECEIVED PING --")
                        self.log("-- SENT PONG --")
                        continue

                    # parse line
                    line = msg.split(" ")
                    username = line[0].replace("!cho@ppy.sh", "")[1:]
                    command = line[1]

                    if command == "PRIVMSG":
                        self.log("--- Received: " + msg)

                    # JOIN, PART, PRIVMSG
                    if command.isalpha():
                        channel = line[2].replace(":", "")
                        if command == "JOIN":
                            if username == self.__username and channel not in self.__channels and "#mp_" in channel:
                                self.__join_helper(channel)
                                self.__new_tournament = channel
                            if channel in self.__channels and not self.__channels[channel].is_game():
                                self.__channels[channel].add_user(username)
                        elif command == "PART":
                            if channel in self.__channels:
                                if self.__channels[channel].is_game():
                                    if self.__channels[channel].get_logic()["on_room_close"]:
                                        x = threading.Thread(target=self.__channels[channel].get_logic()["on_room_close"])
                                        x.setDaemon(True)
                                        x.start()
                                    del self.__channels[channel]
                                elif self.__channels[channel].has_user(username):
                                    self.__channels[channel].del_user(username)
                        elif command == "QUIT":
                            channels = self.__channels.copy()
                            for channel in channels:
                                channels[channel].del_user(username)
                        elif command == "PRIVMSG":
                            content = msg.split(channel + " :", 1)[1]
                            message = {"username": username, "channel": channel, "content": content}
                            # channel messages
                            if channel in self.__channels:
                                self.__channels[channel].process_message(message)
                            # personal messages
                            elif channel == self.__username:
                                if len(self.__personal_message_log) == self.__personal_message_log_length:
                                    self.__personal_message_log = self.__personal_message_log[1:]
                                self.__personal_message_log.append(message)
                                # pass data to front end
                                if message["username"] == "BanchoBot":
                                    if message["content"] == "You cannot create any more tournament matches. Please close any previous tournament matches you have open.":
                                        self.__room_limit_reached = True
                                channels = self.__channels.copy()
                                for channel in channels:
                                    if channels[channel].get_on_personal_message_method():
                                        x = None
                                        if str(inspect.signature(channels[channel].get_on_personal_message_method())).strip("()").split(", ") != [""]:
                                            x = threading.Thread(target=channels[channel].get_on_personal_message_method(), args=(message,))
                                        else:
                                            x = threading.Thread(target=channels[channel].get_on_personal_message_method())
                                        x.setDaemon(True)
                                        x.start()
                                if self.__on_personal_message_method:
                                    x = None
                                    if str(inspect.signature(self.__on_personal_message_method)).strip("()").split(", ") != [""]:
                                        x = threading.Thread(target=self.__on_personal_message_method, args=(message,))
                                    else:
                                        x = threading.Thread(target=self.__on_personal_message_method)
                                    x.setDaemon(True)
                                    x.start()
                                    self.log("-- on personal message method executed --")
                    # functional information
                    else:
                        # users already in channel
                        if command == "353":
                            channel = line[4]
                            if channel in self.__channels:
                                channel = self.__channels[channel]
                                users = line[5:]
                                users[0] = users[0][1:]
                                for username in users:
                                    if username != "" and username[0] != "+" and username[0] != "@":
                                        if channel.is_game():
                                            # game users are added from match history
                                            channel.get_users().append(username)
                                        else:
                                            channel.add_user(username)

                        # invite link
                        elif command == "332":
                            channel = line[3]
                            if channel in self.__channels and self.__channels[channel].is_game():
                                self.__channels[channel].set_invite_link("osump://" + line[-1][1:] + "/")
                        # users already in game channel
                        elif command == "366":
                            channel = line[3]
                            if channel in self.__channels and self.__channels[channel].is_game():
                                self.__channels[channel].get_existing_attributes()
                        # bad credentials
                        elif command == "464":
                            if not self.verbose:
                                print("There was an error connecting to " + self.__host + ":" + str(self.__port))
                                print("Either your username or password is incorrect! Please restart the program.")
                            self.log("There was an error connecting to " + self.__host + ":" + str(self.__port))
                            self.log("Either your username or password is incorrect! Please restart the program.")
                            f = open("config" + os.sep + "bot_config.conf", "r+")
                            config = json.loads(f.read())
                            f.seek(0)
                            f.truncate(0)
                            config["username"] = "username"
                            config["password"] = "password"
                            f.write(json.dumps(config).replace(", ", ",\n").replace("{", "{\n", 1)[:-1] + "\n}")
                            f.close()

    def refresh_logic_profiles(self):
        self.__logic_profiles = {}
        location = os.path.dirname(os.path.realpath(__file__)) + os.sep + "logic_profiles"
        os.path.isdir(location)
        for file in os.listdir(location):
            if file[-3:] == ".py":
                m = importlib.import_module("logic_profiles." + file[:-3])
                for name, obj in inspect.getmembers(m):
                    if inspect.isclass(obj):
                        self.__logic_profiles[obj.__name__] = obj
                        self.__logic_profile_links[obj.__name__] = ""


    # attempts to connect to osu using the provided credentials
    def start(self):
        # grab logic options
        self.refresh_logic_profiles()

        # attempt to auto locate osu directory
        try:
            import winreg
            import shlex
            class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, ".osz")
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(class_root)) as key:
                command = winreg.QueryValueEx(key, '')[0]
                path = shlex.split(command)[0].replace(os.sep + "osu!.exe", "", 1)
                self.set_osu_directory(path)
                self.log("-- Discovered osu directory: '" + path + "' --")
        except:
            self.log("-- Could not discover osu directory! --")

        try:
            self.__sock.get_socket().connect((self.__host, self.__port))
            self.__sock.sendall(("PASS " + self.__password + "\n").encode())
            self.__sock.sendall(("USER " + self.__username + "\n").encode())
            self.__sock.sendall(("NICK " + self.__username + "\n").encode())
            self.log("-- connected to " + self.__host + ":" + str(self.__port) + " successfully --")
            if not self.verbose:
                print("-- connected to " + self.__host + ":" + str(self.__port) + " successfully --")
            self.__listen()
            self.__controller.start()

        except:
            self.log("There was an error connecting to " + self.__host + ":" + str(self.__port))

    # joins a channel and also returns a channel or game object
    def join(self, channel):
        channel = channel.strip()
        if "osu.ppy.sh" in channel:
            channel = "#mp_" + channel.split("/")[-1]
        if channel[0] != "#":
            channel = "#" + channel
        # rejoin bugfix
        self.__sock.sendall(("PART " + channel + "\n").encode())
        return self.__join_helper(channel)

    # splitting join operation fixes rejoining game channels when program is killed
    def __join_helper(self, channel):
        channel = channel.lower()
        if channel not in self.__channels:
            if "#mp_" == channel[:4]:
                self.__channels[channel] = Game(self, channel, self.verbose)
                self.__channels[channel].get_config_link()
            else:
                self.__channels[channel] = Channel(self, channel, self.verbose)
            self.__sock.sendall(("JOIN " + channel + "\n").encode())
            self.log("-- Joined: " + channel + " --")
        return self.__channels[channel]

    # parts a channel
    def part(self, channel):
        if channel[0] != "#":
            channel = "#" + channel
        if channel in self.__channels:
            del self.__channels[channel]
            self.__sock.sendall(("PART " + channel + "\n").encode())
            self.log("-- Parted: " + channel + " --")

    # sends a personal message to a username
    def send_personal_message(self, username, message):
        self.__sock.sendall(("PRIVMSG " + username.replace(" ", "_") + " :" + message + "\n").encode())
        if len(self.__personal_message_log) == self.__personal_message_log_length:
            self.__personal_message_log = self.__personal_message_log[1:]
        self.__personal_message_log.append({"username": self.__username, "channel": username, "content": message})
        self.log("-- sent personal message to " + username + ": '" + message + "' --")

    # adds a broadcast and returns its id, cahnnel can be any channel or username
    def add_broadcast(self, channel, message, secs):
        return self.__broadcast_controller.add_broadcast(channel, message, secs)

    # deletes a broadcast by id
    def del_broadcast(self, id):
        self.__broadcast_controller.del_broadcast(id)

    # returns true if broadcast id is in use
    def has_broadcast_id(self, id):
        return self.__broadcast_controller.has_id(id)

    # returns a broadcast given the id
    def get_broadcast(self, id):
        return self.__broadcast_controller.get_broadcast(id)

    # returns a list of broadcasts int he given channel
    def get_broadcasts(self, channel=""):
        return self.__broadcast_controller.get_broadcasts(channel)

    # makes a tournament lobby and returns the channel object
    def make_room(self, title="", password="", size=16, beatmapID=22538, mods=["ANY"], game_mode="any", team_type="any", scoring_type="any", allow_convert=True, logic_profile="", invite_list=None):
        if invite_list is None:
            invite_list = [self.__username]
        if not title:
            title = self.__username + "'s game"
        self.__make_room_lock.acquire()
        self.__room_limit_reached = False
        self.send_personal_message("BanchoBot", "!mp make " + title)
        while not self.__new_tournament:
            if self.__room_limit_reached:
                self.__make_room_lock.release()
                return
        channel = self.__channels[self.__new_tournament]
        self.__new_tournament = ""
        self.__make_room_lock.release()
        while not channel.get_title():
            pass
        channel.set_allow_convert(allow_convert)
        channel.set_password(password)
        channel.set_size(size)
        channel.set_mods(mods)
        channel.set_team_type(team_type)
        channel.set_scoring_type(scoring_type)
        channel.set_game_mode(game_mode)
        channel.change_beatmap(beatmapID)
        if logic_profile:
            channel.implement_logic_profile(logic_profile)
        for username in invite_list:
            channel.invite_user(username)
        channel.get_config_link()
        return channel

    def logic_profile_upload(self, profile):
        path = inspect.getfile(self.get_logic_profile(profile))
        f = open(path, "r")
        text = f.read()
        f.close()
        self.__logic_profile_links[profile] = self.paste2_upload("OBF3 Logic Profile: " + profile, text)
        return self.__logic_profile_links[profile]

    def logic_profile_download(self, url):
        text = self.paste2_download(url)
        if text:
            description = text.pop(0)
            profile = description.split()[-1]
            if "OBF3 Logic Profile:" in description and profile in text[0]:
                f = open("logic_profiles" + os.sep + profile + ".py", "w")
                f.writelines(text)
                f.close()


    # uploads to paste2.org with passed description and content
    # returns the url of the created paste2 page
    def paste2_upload(self, description, content):
        url = 'https://paste2.org/'
        payload = {
            "code": content,
            "lang": "text",
            "description": description
        }
        r = requests.post(url, data=payload)
        return r.url

    def paste2_download(self, url):
        linesrtn = []
        if "paste2.org" in url:
            if url.find("http") != 0:
                url = "https://" + url
            r = requests.get(url)
            # description is the first value
            linesrtn.append(html.unescape(r.text.split('<div class="desc">', 1)[1].split("</div>", 1)[0].split("<p>", 1)[1][:-4]))

            # main body
            text = r.text.split("<ol class='highlight code'>", 1)[1].split("</div></li></ol>", 1)[0]
            lines = text.split("\n")[1:-1]
            for line in lines:
                linesrtn.append(html.unescape(line.split("<div>", 1)[1].split("</div>", 1)[0]))
        return linesrtn

    def fetch_user_profile(self, username):
        username = str(username).replace(" ", "%20")
        url = "https://osu.ppy.sh/users/" + username
        try:
            r = requests.get(url)
            return json.loads(r.text.split('<script id="json-user" type="application/json">\n            ', 1)[1].split("\n", 1)[0])
        except:
            url = "https://osu.ppy.sh/users/" + username.replace("_", "%20")
            r = requests.get(url)
            return json.loads(r.text.split('<script id="json-user" type="application/json">\n            ', 1)[1].split("\n", 1)[0])

    def set_websocket_port(self, port):
        if not self.__started:
            self.__controller.set_ws_port(port)

    def set_webapp_port(self, port):
        if not self.__started:
            self.__controller.set_webapp_port(port)

    def get_channels(self):
        return self.__channels

    def get_channel(self, channel):
        if channel in self.__channels:
            return self.__channels[channel]

    def has_channel(self, channel):
        return channel in self.__channels

    def get_sock(self):
        return self.__sock

    def get_username(self):
        return self.__username

    def get_broadcast_controller(self):
        return self.__broadcast_controller

    def on_personal_message(self, method):
        self.__on_personal_message_method = method

    def get_logic_profiles(self):
        return self.__logic_profiles

    def get_logic_profile(self, class_name):
        if class_name in self.__logic_profiles:
            return self.__logic_profiles[class_name]

    # implements a logic profile
    def implement_logic_profile(self, profile):
        profile = self.get_logic_profile(profile)(self)
        if hasattr(profile, "on_personal_message") and callable(getattr(profile, "on_personal_message")):
            self.on_personal_message(profile.on_personal_message)

    def format_username(self, username):
        return username.replace(" ", "_")

    def get_personal_message_log(self):
        return self.__personal_message_log

    def get_personal_message_log_length(self):
        return self.__personal_message_log_length

    def set_default_message_log_length(self, length):
        self.__default_message_log_length = length

    def get_default_message_log_length(self):
        return self.__default_message_log_length

    #clones attributes and logic from channel1 to channel2 (strings)
    def clone_channel(self, channel1, channel2):
        attributes = channel1.get_attributes()
        logic = channel1.get_logic_profile()
        channel2.implement_logic_profile(logic)
        channel2.import_attributes(attributes)

    # fetches beatmap from ppy.sh
    def fetch_beatmap(self, beatmapID):
        try:
            beatmapset = self.fetch_parent_set(beatmapID)
        except:
            return {}
        if "beatmaps" in beatmapset:
            for beatmap in beatmapset["beatmaps"]:
                if beatmap["id"] == int(beatmapID):
                    return beatmap
        return {}

    # fetches a beatmapset associated with a beatmapID from ppy.sh
    def fetch_parent_set(self, beatmapID):
        url = "https://osu.ppy.sh/b/" + str(beatmapID)
        r = requests.get(url)
        try:
            return json.loads(
                r.text.split('<script id="json-beatmapset" type="application/json">\n        ', 1)[1].split(
                    "\n", 1)[0])
        except:
            return {}

    def fetch_beatmapset(self, beatmapsetID):
        url = "https://osu.ppy.sh/s/" + str(beatmapsetID)
        r = requests.get(url)
        try:
            return json.loads(
                r.text.split('<script id="json-beatmapset" type="application/json">\n        ', 1)[1].split(
                    "\n", 1)[0])
        except:
            return {}

    def set_player_blacklist(self, blacklist):
        self.__player_blacklist = blacklist
        channels = self.__channels.copy()
        for channel in channels:
            if channels[channel].is_game():
                channels[channel].set_player_blacklist(blacklist)

    def add_player_blacklist(self, username):
        if username.replace(" ", "_") not in self.get_formatted_player_blacklist():
            self.__player_blacklist.append(username)
            channels = self.__channels.copy()
            for channel in channels:
                if channels[channel].is_game():
                    channels[channel].add_player_blacklist(username)

    def del_player_blacklist(self, username):
        if username.replace(" ", "_") in self.get_formatted_player_blacklist():
            del self.__player_blacklist[self.get_formatted_player_blacklist().index(username.replace(" ", "_"))]
            channels = self.__channels.copy()
            for channel in channels:
                if channels[channel].is_game():
                    channels[channel].del_player_blacklist(username)

    def get_player_blacklist(self):
        return self.__player_blacklist

    def get_formatted_player_blacklist(self):
        return [x.replace(" ", "_") for x in self.__player_blacklist]

    def set_verbose(self, status):
        self.verbose = status

    def set_logging(self, status):
        self.logging = status
        if not status:
            self.__logger.close()

    def _get_controller(self):
        return self.__controller

    def exit_handler(self):
        self.log("-- Ran exit handler --")
        for channel in self.__channels.copy():
            self.part(channel)
        self.set_logging(False)
        self.__started = False
        self.__controller.stop()
        sys.exit(0)

    def get_password(self):
        return self.__password

    def set_osu_directory(self, path):
        if path:
            path = path.replace("/", os.sep).replace("\\", os.sep)
            if path[-1] == os.sep:
                path = path[:-1]

        self.__osu_directory = path
        if path:
            self.chimu.set_songs_directory(path + os.sep + "Songs")
        else:
            self.chimu.set_songs_directory("")

    def get_osu_directory(self):
        return self.__osu_directory

    def set_authenticate(self, status):
        self.__authenticate = status

    def is_authenticate(self):
        return self.__authenticate
