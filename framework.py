import importlib
import inspect
import json
import os
import threading
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
        self.__controller = Controller(self, host=server_ip)
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
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
        self.__player_blacklist = []
        self.chimu = Chimu(self)
        self.__logger = Logger("config" + os.sep + "logs" + os.sep + str(datetime.now()).replace(" ", "_", 1).replace(":", "-").split(".", 1)[0] + ".txt", "a")
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
            while True:
                # add to the buffer every loop
                data = self.__sock.get_socket().recv(2048)
                buffer += data.decode("utf-8").replace("\r", "")
                # while there are messages
                while "\n" in buffer:
                    line = buffer[:buffer.find("\n")]
                    buffer = buffer.replace(line + "\n", "", 1)

                    # ping pong
                    if line[:4] == "PING":
                        self.__sock.sendall((line.replace("PING", "PONG") + "\n").encode())
                        if self.verbose or self.logging:
                            self.log("-- RECEIVED PING --")
                            self.log("-- SENT PONG --")
                        continue

                    # parse line
                    line = line.split(" ")
                    username = line[0].replace("!cho@ppy.sh", "")[1:]
                    command = line[1]
                    if command != "QUIT" and (self.verbose or self.logging):
                        self.log("--- Received: " + " ".join(line))

                    # JOIN, PART, PRIVMSG
                    if command.isalpha():
                        if command != "QUIT":
                            channel = line[2].replace(":", "")
                            if command == "JOIN":
                                if username == self.__username and channel not in self.__channels and "#mp_" in channel:
                                    self.join(channel)
                                    self.__new_tournament = channel
                                if channel in self.__channels and not self.__channels[channel].is_game():
                                    self.__channels[channel].add_user(username)
                            elif command == "PART":
                                if channel in self.__channels:
                                    if self.__channels[channel].is_game():
                                        del self.__channels[channel]
                                    elif username in self.__channels[channel].get_formatted_users():
                                        self.__channels[channel].del_user(username)
                            elif command == "PRIVMSG":
                                content = " ".join(line[3:]).replace(":", "", 1)
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
                                    for channel in self.__channels:
                                        if self.__channels[channel].get_on_personal_message_method():
                                            if len(str(inspect.signature(self.__channels[channel].get_on_personal_message_method())).strip("()").split(", ")) == 1:
                                                threading.Thread(target=self.__channels[channel].get_on_personal_message_method(), args=(message,)).start()
                                            else:
                                                threading.Thread(target=self.__channels[channel].get_on_personal_message_method()).start()
                                    if self.__on_personal_message_method:
                                        if len(str(inspect.signature(self.__on_personal_message_method)).strip("()").split(", ")) == 1:
                                            threading.Thread(target=self.__on_personal_message_method, args=(message,)).start()
                                        else:
                                            threading.Thread(target=self.__on_personal_message_method).start()
                            self.__controller.update()
                    # functional information
                    else:
                        # users already in channel
                        if command == "353":
                            channel = line[4]
                            if channel in self.__channels:
                                users = line[5:]
                                users[0] = users[0][1:]
                                for username in users:
                                    if username != "" and username[0] != "+" and username[0] != "@":
                                        if self.__channels[channel].is_game():
                                            # game users are added from match history
                                            self.__channels[channel].get_users().append(username)
                                        else:
                                            self.__channels[channel].add_user(username)

                        # invite link
                        elif command == "332":
                            channel = line[3]
                            if self.__channels[channel].is_game():
                                self.__channels[channel].set_invite_link("osump://" + line[-1][1:] + "/")
                        # users already in game channel
                        elif command == "366" :
                            channel = line[3]
                            if channel in self.__channels and self.__channels[channel].is_game():
                                self.__channels[channel].get_existing_attributes()
                            self.__controller.update()

    # attempts to connect to osu using the provided credentials
    def start(self):
        # grab logic options
        location = os.path.dirname(os.path.realpath(__file__)) + os.sep + "logic_profiles"
        os.path.isdir(location)
        for file in os.listdir(location):
            if file[-3:] == ".py":
                m = importlib.import_module("logic_profiles." + file[:-3])
                for name, obj in inspect.getmembers(m):
                    if inspect.isclass(obj):
                        self.__logic_profiles[obj.__name__] = obj

        try:
            self.__sock.get_socket().connect((self.__host, self.__port))
            self.__sock.sendall(("PASS " + self.__password + "\n").encode())
            self.__sock.sendall(("USER " + self.__username + "\n").encode())
            self.__sock.sendall(("NICK " + self.__username + "\n").encode())
            if self.verbose or self.logging:
                self.log("-- connected to " + self.__host + ":" + str(self.__port) + " successfully --")
            self.__listen()
            self.__controller.start()

        except:
            self.log("There was an error connecting to " + self.__host + ":" + str(self.__port))

    # joins a channel and also returns a channel or game object
    def join(self, channel):
        if channel[0] != "#":
            channel = "#" + channel
        if channel not in self.__channels:
            if "#mp_" == channel[:4]:
                self.__channels[channel] = Game(self, channel, self.verbose)
            else:
                self.__channels[channel] = Channel(self, channel, self.verbose)
            self.__sock.sendall(("JOIN " + channel + "\n").encode())
        return self.__channels[channel]

    # parts a channel
    def part(self, channel):
        if channel[0] != "#":
            channel = "#" + channel
        if channel in self.__channels:
            del self.__channels[channel]
            self.__sock.sendall(("PART :" + channel + "\n").encode())

    # sends a personal message to a username
    def send_personal_message(self, username, message):
        self.__sock.sendall(("PRIVMSG " + username.replace(" ", "_") + " :" + message + "\n").encode())
        if len(self.__personal_message_log) == self.__personal_message_log_length:
            self.__personal_message_log = self.__personal_message_log[1:]
        self.__personal_message_log.append({"username": self.__username, "channel": username, "content": message})
        if self.verbose or self.logging:
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
    def make_room(self, title="game room", password="", size=8, beatmapID=22538, mods=["ANY"], game_mode="any", team_type="any", scoring_type="any", allow_convert=False):
        self.__make_room_lock.acquire()
        self.__room_limit_reached = False
        self.send_personal_message("BanchoBot", "!mp make " + title)
        while not self.__new_tournament:
            if self.__room_limit_reached:
                return
        channel = self.__channels[self.__new_tournament]
        self.__new_tournament = ""
        self.__make_room_lock.release()
        while not channel.get_invite_link():
            pass
        channel.set_allow_convert(allow_convert)
        channel.set_password(password)
        channel.set_size(size)
        channel.set_mods(mods)
        channel.set_game_mode(game_mode)
        channel.set_team_type(team_type)
        channel.set_scoring_type(scoring_type)
        if beatmapID != 22538:
            channel.change_beatmap(beatmapID)
        self.send_personal_message(self.__username, self.__username + " a game room was created: [" + channel.get_invite_link() + " " + title + "]")
        return channel


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

    def fetch_user_profile(self, username):
        url = "https://osu.ppy.sh/users/" + str(username).replace(" ", "%20")
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
    def implement_logic(self, profile):
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
        attributes = self.__channels[channel1].get_attributes()
        logic = self.__channels[channel1].get_logic_profile()
        self.__channels[channel2].implement_logic_profile(logic)
        self.__channels[channel2].import_attributes(attributes)

    # fetches beatmap from ppy.sh
    def fetch_beatmap(self, beatmapID):
        try:
            beatmapset = self.fetch_beatmapset(beatmapID)
        except:
            return {}
        if "beatmaps" in beatmapset:
            for beatmap in beatmapset["beatmaps"]:
                if beatmap["id"] == int(beatmapID):
                    return beatmap
        return {}

    # fetches a beatmapset associated with a beatmapID from ppy.sh
    def fetch_beatmapset(self, beatmapID):
        url = "https://osu.ppy.sh/b/" + str(beatmapID)
        r = requests.get(url)
        try:
            return json.loads(
                r.text.split('<script id="json-beatmapset" type="application/json">\n        ', 1)[1].split(
                    "\n", 1)[0])
        except:
            return {}

    def set_player_blacklist(self, blacklist):
        self.__player_blacklist = blacklist
        for channel in self.__channels:
            if self.__channels[channel].is_game():
                self.__channels[channel].set_player_blacklist(blacklist)

    def add_player_blacklist(self, username):
        if username.replace(" ", "_") not in self.get_formatted_player_blacklist():
            self.__player_blacklist.append(username)
            for channel in self.__channels:
                if self.__channels[channel].is_game():
                    self.__channels[channel].add_player_blacklist(username)

    def del_player_blacklist(self, username):
        if username.replace(" ", "_") in self.get_formatted_player_blacklist():
            del self.__player_blacklist[self.get_formatted_player_blacklist().index(username.replace(" ", "_"))]
            for channel in self.__channels:
                if self.__channels[channel].is_game():
                    self.__channels[channel].del_player_blacklist(username)

    def get_player_blacklist(self):
        return self.__player_blacklist

    def get_formatted_player_blacklist(self):
        return [x.replace(" ", "_") for x in self.__player_blacklist]

    def set_verbose(self, status):
        self.verbose = status

    def set_logging(self, status):
        self.logging = status