import copy
import importlib
import inspect
import json
import os
import threading

from broadcast_controller import BroadcastController
from channel import Channel
from game import Game
from socket_wrapper import Sock
from webapp.controller import Controller
import requests
from requests.structures import CaseInsensitiveDict


class Bot:
    def __init__(self, username="", password="", host="irc.ppy.sh", port=6667, server_ip="localhost", verbose=False):
        self.__sock = Sock()
        self.__controller = Controller(self, host=server_ip)
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__started = False
        self.__channels = {}
        self.__personal_message_log = []
        self.__personal_message_log_length = 50
        self.__room_limit_reached = False
        self.__make_room_lock = threading.Lock()
        self.__new_tournament = ""
        self.__broadcast_controller = BroadcastController(self)
        self.__on_personal_message_method = None
        self.__logic_profiles = {}
        self.verbose = verbose

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
                        if self.verbose:
                            print("-- SENT PONG --")
                        continue

                    # parse line
                    line = line.split(" ")
                    username = line[0].replace("!cho@ppy.sh", "")[1:]
                    command = line[1]
                    if command != "QUIT" and self.verbose:
                        print("--- Received: " + " ".join(line))

                    # JOIN, PART, PRIVMSG
                    if command.isalpha():
                        if command != "QUIT":
                            channel = line[2].replace(":", "")
                            if command == "JOIN":
                                if username == self.__username and channel not in self.__channels and "#mp_" in channel:
                                    self.join(channel)
                                    self.__new_tournament = channel
                                if channel in self.__channels:
                                    self.__channels[channel].add_user(username)
                            elif command == "PART":
                                if channel in self.__channels:
                                    self.__channels[channel].del_user(username)
                                    if self.__channels[channel].is_game():
                                        del self.__channels[channel]
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
                                            threading.Thread(target=self.__channels[channel].get_on_personal_message_method(), args=(message,)).start()
                                    if self.__on_personal_message_method:
                                        threading.Thread(target=self.__on_personal_message_method, args=(message,)).start()
                            self.__controller.update()
                    # functional information
                    else:
                        # users already in channel
                        if command == "353":
                            channel = line[4]
                            if channel in self.__channels and not self.__channels[channel].is_game():
                                users = line[5:]
                                users[0] = users[0][1:]
                                for username in users:
                                    if username != "" and username[0] != "+" and username[0] != "@" and username != "BanchoBot":
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
        try:
            # grab logic options
            location = os.path.dirname(os.path.realpath(__file__)) + os.sep + "logic_profiles"
            os.path.isdir(location)
            for file in os.listdir(location):
                if file[-3:] == ".py":
                    m = importlib.import_module("logic_profiles." + file[:-3])
                    for name, obj in inspect.getmembers(m):
                        if inspect.isclass(obj):
                            self.__logic_profiles[obj.__name__] = obj


            self.__sock.get_socket().connect((self.__host, self.__port))
            self.__sock.sendall(("PASS " + self.__password + "\n").encode())
            self.__sock.sendall(("USER " + self.__username + "\n").encode())
            self.__sock.sendall(("NICK " + self.__username + "\n").encode())
            if self.verbose:
                print("-- connected to " + self.__host + ":" + str(self.__port) + " successfully --")
            self.__listen()
            self.__controller.start()

        except:
            print("There was an error connecting to", self.__host + ":" + str(self.__port))

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
        if self.verbose:
            print("-- sent personal message to " + username + ": '" + message + "' --")

    # adds a broadcast and returns its id, cahnnel can be any channel or username
    def add_broadcast(self, channel, message, secs):
        return self.__broadcast_controller.add_broadcast(channel, message, secs)

    # deletes a broadcast by id
    def del_broadcast(self, id):
        self.__broadcast_controller.del_broadcast(id)

    def make_room(self, title="game room", password="", size=8):
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
        channel.set_password(password)
        channel.set_size(size)
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

    #clones attributes and logic from channel1 to channel2 (strings)
    def clone_channel(self, channel1, channel2):
        attributes = self.__channels[channel1].get_attributes()
        logic = self.__channels[channel1].get_logic_profile()
        self.__channels[channel2].implement_logic_profile(logic)
        self.__channels[channel2].import_attributes(attributes)

    # fetches beatmap from ppy.sh
    def fetch_beatmap(self, beatmapID):
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
        url = "https://osu.ppy.sh/b/" + str(beatmapID)
        r = requests.get(url)
        try:
            return json.loads(
                r.text.split('<script id="json-beatmapset" type="application/json">\n        ', 1)[1].split(
                    "\n", 1)[0])
        except:
            return {}