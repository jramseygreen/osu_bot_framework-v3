import json
import socket
import threading

import requests

from tools import crypto
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
        self.__current_user_profile = {"username": "", "avatar_url": "", "country_code": "gb", "statistics": {"level": {"current": 0}, "global_rank": 0, "pp": 0, "hit_accuracy": 0, "play_count": 0}}
        self.__making_room = False
        self.crypto = crypto.CryptoWrapper(bot.get_password())

    def __on_message(self, conn, msg):
        if msg == "é" or msg == "\x03é":
            return

        if self.bot.is_authenticate():
            msg = self.crypto.decrypt(msg)

        data = {}
        try:
            data = json.loads(msg)
            if not data["command"] == "update":
                self.bot.log("-- webapp sent: " + msg + " --")
        except:
            if self.bot.is_authenticate():
                self.send_message("authenticate", conn)
            return
        if data["command"] == "exit_handler":
            self.bot.exit_handler()
        elif data["command"] == "update":
            self.update(conn)
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
                                    x = threading.Thread(target=channel.get_logic()["on_match_abort"])
                                    x.setDaemon(True)
                                    x.start()
                                    self.bot.log("-- on match abort method executed --")
        elif data["command"] == "personal_message":
            if data["message"]:
                self.bot.send_personal_message(data["channel"], data["message"])
        elif data["command"] == "make_room":
            self.__making_room = True
            self.bot.make_room(title=data["title"], password=data["password"], game_mode=data["game_mode"], scoring_type=data["scoring_type"], team_type=data["team_type"], logic_profile=data["logic_profile"], invite_list=data["invite_list"], beatmapID=data["beatmapID"], size=data["size"])
            self.__making_room = False
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
        elif data["command"] == "del_beatmap_blacklist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.del_beatmap_blacklist(data["beatmapID"])
        elif data["command"] == "del_beatmap_whitelist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.del_beatmap_whitelist(data["beatmapID"])
        elif data["command"] == "add_beatmap_blacklist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.add_beatmap_blacklist(data["beatmapID"])
        elif data["command"] == "add_beatmap_whitelist":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.add_beatmap_whitelist(data["beatmapID"])
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
                channel.auto_download(data["auto_download"], data["auto_download_path"], data["auto_open"], data["download_video"])
            self.bot.set_osu_directory(data["osu_directory"])
            self.bot.chimu.set_redownload(data["redownload_owned_beatmaps"])
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
        elif data["command"] == "set_ar_range":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_ar_range(data["range"])
        elif data["command"] == "set_od_range":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_od_range(data["range"])
        elif data["command"] == "set_cs_range":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_cs_range(data["range"])
        elif data["command"] == "set_hp_range":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_hp_range(data["range"])
        elif data["command"] == "set_bpm_range":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_bpm_range(data["range"])
        elif data["command"] == "set_length_range":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_length_range(data["range"])
        elif data["command"] == "set_diff_range":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_diff_range(data["range"])
        elif data["command"] == "set_size":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.set_size(data["size"])
        elif data["command"] == "import_config":
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.import_config(data["url"])
        elif data["command"] == "clone_channel":
            channel1 = self.bot.get_channel(data["channel1"])
            channel2 = self.bot.get_channel(data["channel2"])
            self.bot.clone_channel(channel1, channel2)
        elif data["command"] == "refresh_logic_profiles":
            self.bot.refresh_logic_profiles()
        elif data["command"] == "del_logic_profile":
            self.bot.del_logic_profile(data["profile"])
        elif data["command"] == "download_logic_profile":
            self.bot.logic_profile_download(data["url"])
        elif data["command"] == "get_logic_profile_link":
            self.bot.get_logic_profile_link(data["profile"])
        elif data["command"] == "authenticate":
            self.send_message("success", conn)

        if "channel" in data:
            channel = self.bot.get_channel(data["channel"])
            if channel and channel.is_game():
                channel.get_config_link()

    def start(self, running=False):
        if not running:
            x = threading.Thread(target=self.start, args=(True,))
            x.setDaemon(True)
            x.start()
        else:
            # start websocket server
            self.__ws.listen()

            # start webapp server
            self.__webapp_sock.bind((self.__host, self.__webapp_port))
            self.__webapp_sock.listen()
            # self.__update_loop()
            self.bot.log("-- Webapp server started at http://" + self.__host + ":" + str(self.__webapp_port) + "/ --")
            if not self.bot.verbose:
                print("-- Webapp server started at http://" + self.__host + ":" + str(self.__webapp_port) + "/ --")
            ws_host = self.__ws.get_host()
            if ws_host == "0.0.0.0":
                try:
                    ws_host = requests.get('https://checkip.amazonaws.com').text.strip()
                except:
                    pass
            while True:
                try:
                    conn, addr = self.__webapp_sock.accept()
                    conn.recv(1024)
                    # header
                    text = 'HTTP/1.0 200 OK\n'
                    text += 'Content-Type: text/html\n'
                    text += 'Content-Type: text/html\n\n'
                    f = open("webapp/index.html", "r", encoding="utf8")
                    text += f.read()
                    f.close()
                    text = text.replace("ws://localhost:9876", "ws://" + ws_host + ":" + str(self.__ws.get_port()), 1)
                    try:
                        conn.sendall(text.encode())
                    except ConnectionAbortedError:
                        pass
                    conn.close()
                except OSError:
                    return

    def send_message(self, message, conn=None):
        if not conn:
            for conn in self.__ws.get_clients():
                if self.bot.is_authenticate() and not message == "authenticate" and not message == "success":
                    message = self.crypto.encrypt(message)
                self.__ws.send(conn, message)
        else:
            if self.bot.is_authenticate() and not message == "authenticate" and not message == "success":
                message = self.crypto.encrypt(message)
            self.__ws.send(conn, message)

    def update(self, conn=None):
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
        data["logic_profile_links"] = self.bot.get_logic_profile_links()
        data["current_user_profile"] = self.__current_user_profile
        data["bot_username"] = self.bot.get_username()
        data["redownload_owned_beatmaps"] = self.bot.chimu.is_redownload()
        data["osu_directory"] = self.bot.get_osu_directory()
        data["making_room"] = self.__making_room
        self.send_message(json.dumps(data), conn)

    def set_ws_port(self, port):
        self.__ws.set_port(port)

    def set_webapp_port(self, port):
        self.__webapp_port = port

    def stop(self):
        self.__ws.stop()
        self.__webapp_sock.close()