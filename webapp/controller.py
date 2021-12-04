import json
import os
import socket
import threading
import time

import requests

from webapp.ws_server import ws_server


class Controller:
    def __init__(self, bot, host="localhost", ws_port=9876, webapp_port=80, on_message_function=None):
        self.bot = bot
        self.__host = host
        if not on_message_function:
            on_message_function = self.__on_message
        self.__ws = ws_server(host=host, port=ws_port, on_message_function=on_message_function)
        self.__webapp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__webapp_port = webapp_port
        self.__user_num = 20
        self.__current_user_profile = {"username": "", "avatar_url": "", "country_code": "", "statistics": {"level": {"current": 0}, "global_rank": 0, "pp": 0, "hit_accuracy": 0}}

    def __on_message(self, conn, msg):
        print(msg)
        data = json.loads(msg)
        if data["command"] == "exit_handler":
            self.bot.exit_handler()
        elif data["command"] == "update":
            self.update()
        elif data["command"] == "set_user_num":
            self.__user_num = data["user_num"]
        elif data["command"] == "start_match":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.start_match()
        elif data["command"] == "abort_match":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.abort_match()
        elif data["command"] == "channel_message":
            data["message"] = data["message"].strip()
            if data["message"]:
                channel = self.bot.get_channel(data["channel"])
                if channel:
                    channel.send_message(data["message"])
                    if channel.is_game():
                        message_arr = data["message"].lower().split(" ")
                        if len(message_arr) >= 2:
                            command = " ".join(message_arr[:2]).strip()
                            args = message_arr[2:]
                            if command == "!mp addref":
                                for arg in args:
                                    if arg not in channel.get_referees():
                                        channel.add_referee(arg)
                            elif command == "!mp removeref":
                                for username in args:
                                    if username != channel.get_creator().replace(" ", "_") and username in channel.get_referees():
                                        channel.del_referee(username)
                                        if username == self.bot.get_username():
                                            self.bot.part(data["channel"])
                            elif command == "!mp password":
                                channel.set_invite_link(channel.get_invite_link().replace(channel.get_password(), ""))
                                if args:
                                    channel._password = args[0]
                                    channel.set_invite_link(channel.get_invite_link() + args[0])
                                else:
                                    channel._password = ""
                            elif command == "!mp size":
                                if args:
                                    channel._size = int(args[0])
                            elif command == "!abort" and channel.in_progress():
                                if channel.get_logic()["on_match_abort"]:
                                    threading.Thread(target=channel.get_logic()["on_match_abort"]).start()
                                    self.bot.log("-- on match abort method executed --")
        elif data["command"] == "personal_message":
            if data["message"]:
                self.bot.send_personal_message(data["channel"], data["message"])
        elif data["command"] == "make_room":
            self.bot.make_room(title=data["title"], password=data["password"], game_mode=data["game_mode"], scoring_type=data["scoring_type"], team_type=data["team_type"])
        elif data["command"] == "join":
            self.bot.join(data["channel"])
        elif data["command"] == "part":
            self.bot.part(data["channel"])
        elif data["command"] == "set_logic_profile":
            channel = self.bot.get_channel(data["channel"])
            if channel:
                channel.implement_logic_profile(data["profile"])
        elif data["command"] == "close_room":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.close_room()
        elif data["command"] == "set_game_mode":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_game_mode(data["game_mode"])
        elif data["command"] == "set_team_type":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_team_type(data["team_type"])
        elif data["command"] == "set_scoring_type":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_scoring_type(data["scoring_type"])
        elif data["command"] == "set_mods":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_mods(data["mods"])
        elif data["command"] == "set_map_status":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_map_status(data["map_status"])
        elif data["command"] == "set_host":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_host(data["username"])
        elif data["command"] == "kick_user":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.kick_user(data["username"])
        elif data["command"] == "set_title":
            if data["title"]:
                channel = self.bot.get_channel(data["channel"])
                if channel and channel.is_game():
                    channel.set_title(data["title"])
        elif data["command"] == "add_broadcast":
            channel = self.bot.get_channel(data["channel"])
            if channel:
                channel.add_broadcast(data["message"], data["secs"])
        elif data["command"] == "del_broadcast":
            channel = self.bot.get_channel(data["channel"])
            if channel:
                channel.del_broadcast(data["broadcast_id"])
        elif data["command"] == "add_player_blacklist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                if data["global"]:
                    self.bot.add_player_blacklist(data["username"])
                else:
                    channel.add_player_blacklist(data["username"])
        elif data["command"] == "del_player_blacklist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.del_player_blacklist(data["username"])
        elif data["command"] == "del_artist_whitelist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.del_artist_whitelist(data["artist"])
        elif data["command"] == "del_artist_blacklist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.del_artist_blacklist(data["artist"])
        elif data["command"] == "del_creator_whitelist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.del_beatmap_creator_whitelist(data["creator"])
        elif data["command"] == "del_creator_blacklist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.del_beatmap_creator_blacklist(data["creator"])
        elif data["command"] == "add_artist_whitelist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.add_artist_whitelist(data["artist"])
        elif data["command"] == "add_artist_blacklist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.add_artist_blacklist(data["artist"])
        elif data["command"] == "add_creator_whitelist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.add_beatmap_creator_whitelist(data["creator"])
        elif data["command"] == "add_creator_blacklist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.add_beatmap_creator_blacklist(data["creator"])
        elif data["command"] == "set_advanced_options":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_beatmap_checker(data["beatmap_checker"])
                channel.set_allow_convert(data["allow_convert"])
                channel.set_allow_unsubmitted(data["allow_unsubmitted"])
                channel.maintain_title(data["maintain_title"])
                channel.maintain_password(data["maintain_password"])
                channel.maintain_size(data["maintain_size"])
                channel.start_on_players_ready(data["autostart"])
                channel.set_autostart_timer(True, data["autostart_timer"])
                channel.set_welcome_message(data["welcome_message"])
        elif data["command"] == "set_password":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_password(data["password"])
        elif data["command"] == "fetch_user_profile":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                if self.__current_user_profile["username"] != data["username"]:
                    self.__current_user_profile = self.bot.fetch_user_profile(data["username"])
                    self.__current_user_profile["country_code"] = self.__current_user_profile["country_code"].lower()

        if "channel" in data:
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.get_config_link()

    def start(self, running=False):
        if not running:
            threading.Thread(target=self.start, args=(True,)).start()
        else:
            # start websocket server
            self.__ws.listen()

            # start webapp server
            self.__webapp_sock.bind((self.__host, self.__webapp_port))
            self.__webapp_sock.listen()
            self.__update_loop()
            self.bot.log("-- Webapp server started at http://" + self.__host + ":" + str(self.__webapp_port) + "/ --")
            ws_host = self.__ws.get_host()
            if ws_host == "0.0.0.0":
                try:
                    ws_host = requests.get('https://checkip.amazonaws.com').text.strip()
                except:
                    pass
            while True:
                conn, addr = self.__webapp_sock.accept()
                conn.recv(1024)
                # header
                text = 'HTTP/1.0 200 OK\n'
                text += 'Content-Type: text/html\n'
                text += 'Content-Type: text/html\n\n'
                f = open("webapp/index2.html", "r", encoding="utf8")
                text += f.read()
                f.close()
                text = text.replace("ws://localhost:9876", "ws://" + ws_host + ":" + str(self.__ws.get_port()), 1)
                try:
                    conn.sendall(text.encode())
                except ConnectionAbortedError:
                    pass
                conn.close()

    def send_message(self, message):
        for conn in self.__ws.get_clients():
            self.__ws.send(conn, message)

    def update(self):
        try:
            data = {"channels": {}}
            channels = self.bot.get_channels().copy()
            for channel in channels:
                data["channels"][channel] = channels[channel].get_attributes()
                data["channels"][channel]["total_users"] = len(data["channels"][channel]["users"])
                data["channels"][channel]["users"] = data["channels"][channel]["users"][:self.__user_num]
                if "mp_" in channel:
                    data["channels"][channel]["host"] = channels[channel].get_host()
                else:
                    data["channels"][channel]["host"] = ""
                    data["channels"][channel]["in_progress"] = False
                    data["channels"][channel]["slots"] = {int(data["channels"][channel]["users"].index(user)): {"username": user} for user in data["channels"][channel]["users"]}
                if "commands" in data["channels"][channel]:
                    del data["channels"][channel]["commands"]
            data["pm"] = self.bot.get_personal_message_log()
            data["logic_profiles"] = list(self.bot.get_logic_profiles().keys())
            data["current_user_profile"] = self.__current_user_profile
            self.send_message(json.dumps(data))
        except:
            pass

    def __update_loop(self, running=False):
        if not running:
            threading.Thread(target=self.__update_loop, args=(True,)).start()
        else:
            while True:
                time.sleep(1)
                self.update()

    def set_ws_port(self, port):
        self.__ws.set_port(port)

    def set_webapp_port(self, port):
        self.__webapp_port = port
