import json
import os
import socket
import threading
import time

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

    def __on_message(self, conn, msg):
        data = json.loads(msg.lower())
        if data["command"] == "update":
            self.update()
        elif data["command"] == "start_match":
            self.bot.get_channel(data["channel"]).start_match()
        elif data["command"] == "abort_match":
            self.bot.get_channel(data["channel"]).abort_match()
        elif data["command"] == "send_message":
            self.bot.get_channel(data["channel"]).send_message(data["message"])

    def start(self, running=False):
        if not running:
            threading.Thread(target=self.start, args=(True,)).start()
        else:
            # start websocket server
            self.__ws.listen()

            # start webapp server
            self.__webapp_sock.bind((self.__host, self.__webapp_port))
            self.__webapp_sock.listen()
            if self.bot.verbose:
                print("-- Webapp server started --")
            while True:
                conn, addr = self.__webapp_sock.accept()
                conn.recv(1024)
                # header
                index = open("webapp/index2.html", "r", encoding="utf8")
                text = 'HTTP/1.0 200 OK\n'
                text += 'Content-Type: text/html\n'
                text += 'Content-Type: text/html\n\n'
                text += index.read()
                index.close()
                try:
                    conn.sendall(text.encode())
                except ConnectionAbortedError:
                    pass
                conn.close()

    def send_message(self, message):
        for conn in self.__ws.get_clients():
            self.__ws.send(conn, message)

    def update(self):
        time.sleep(1.2)
        data = {"channels": {}}
        for channel in self.bot.get_channels():
            data["channels"][channel] = self.bot.get_channel(channel).get_attributes()
            if "mp_" in channel:
                data["channels"][channel]["host"] = self.bot.get_channel(channel).get_host()
            else:
                data["channels"][channel]["host"] = ""
                data["channels"][channel]["in_progress"] = False
                data["channels"][channel]["slots"] = {int(data["channels"][channel]["users"].index(user)): {"username": user} for user in data["channels"][channel]["users"]}
            if "commands" in data["channels"][channel]:
                del data["channels"][channel]["commands"]
        data["pm"] = self.bot.get_personal_message_log()
        data["logic_profiles"] = list(self.bot.get_logic_profiles().keys())
        self.send_message(json.dumps(data))

    def set_ws_port(self, port):
        self.__ws.set_port(port)

    def set_webapp_port(self, port):
        self.__webapp_port = port
