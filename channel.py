import inspect
import threading

from tools.common_commands import CommonCommands
from tools.vote_manager import Vote


class Channel:
    def __init__(self, bot, channel, verbose):
        self._bot = bot
        self._channel = channel
        self._message_log = []
        self._message_log_length = bot.get_default_message_log_length()
        self._users = []
        self._commands = {}
        self.verbose = verbose
        self._logic_profile = ""
        self.common_commands = CommonCommands(bot, self)

        # on_event methods
        self.__on_personal_message_method = None
        self.__on_join_method = None
        self.__on_part_method = None
        self.__on_message_method = None

    def add_user(self, username):
        if username not in self.get_users():
            self._users.append(username)
            self._bot.log("-- Added user: " + username + " to: " + self._channel + " --")
            if self.__on_join_method:
                slot = None
                if self.is_game():
                    slot = self.get_slot_num(username)
                argnum = len(str(inspect.signature(self.__on_join_method)).strip("()").split(", "))
                x = None
                if argnum == 2:
                    x = threading.Thread(target=self.__on_join_method, args=(username, slot,))
                elif str(inspect.signature(self.__on_join_method)).strip("()").split(", ") != [""]:
                    x = threading.Thread(target=self.__on_join_method, args=(username,))
                else:
                    x = threading.Thread(target=self.__on_join_method)
                x.setDaemon(True)
                x.start()
                self._bot.log("-- on join method executed --")

    def del_user(self, username):
        if self.has_user(username):
            slot = None
            if self.is_game():
                slot = self.get_slot_num(username)
            del self._users[self.get_formatted_users().index(username.replace(" ", "_"))]
            self._bot.log("-- Removed user: " + username + " from: " + self._channel + " --")
            if self.__on_part_method:
                argnum = len(str(inspect.signature(self.__on_part_method)).strip("()").split(", "))
                x = None
                if argnum == 2:
                    x = threading.Thread(target=self.__on_part_method, args=(username, slot,))
                elif str(inspect.signature(self.__on_part_method)).strip("()").split(", ") != [""]:
                    x = threading.Thread(target=self.__on_part_method, args=(username,))
                else:
                    x = threading.Thread(target=self.__on_part_method)
                x.setDaemon(True)
                x.start()
                self._bot.log("-- on part method executed --")

    def process_message(self, message):
        if len(self._message_log) == self._message_log_length:
            self._message_log = self._message_log[1:]
        self._message_log.append(message)
        if self.__on_message_method:
            x = None
            if str(inspect.signature(self.__on_message_method)).strip("()").split(", ") != [""]:
                x = threading.Thread(target=self.__on_message_method, args=(message,))
            else:
                x = threading.Thread(target=self.__on_message_method)
            x.setDaemon(True)
            x.start()
            self._bot.log("-- on message method executed --")

    def send_message(self, message):
        message = message.strip()
        self._bot.get_sock().sendall(("PRIVMSG " + self._channel + " :" + str(message) + "\n").encode())
        if len(self._message_log) == self._message_log_length:
            self._message_log = self._message_log[1:]
        self._message_log.append({"username": self._bot.get_username().replace(" ", "_"), "channel": self._channel, "content": message})
        self._bot._get_controller().update()
        self._bot.log("-- sent message to " + self._channel + ": '" + str(message) + "' --")

    def is_game(self):
        return self._channel[:4] == "#mp_"

    def get_channel(self):
        return self._channel

    def get_users(self):
        return self._users

    def get_formatted_users(self):
        return self._users

    def set_message_log_length(self, length):
        self._message_log_length = length

    def set_command(self, command, response, description=""):
        self._commands[command] = {"response": response, "description": description}

    def get_message_log(self, username=""):
        if username:
            message_log = []
            for message in self._message_log.copy():
                if message["username"] == username.replace(" ", "_"):
                    message_log.append(message)
            return message_log
        return self._message_log.copy()

    # adds a broadcast in this channel and returns its id
    def add_broadcast(self, message, secs):
        return self._bot.get_broadcast_controller().add_broadcast(self._channel, message, secs)

    def del_broadcast(self, id):
        self._bot.del_broadcast(id)

    def get_on_personal_message_method(self):
        return self.__on_personal_message_method

    def on_personal_message(self, method):
        self.__on_personal_message_method = method

    def on_join(self, method):
        self.__on_join_method = method

    def on_part(self, method):
        self.__on_part_method = method

    def on_message(self, method):
        self.__on_message_method = method
        
    def implement_logic_profile(self, profile):
        if profile == "" or profile in self._bot.get_logic_profiles():
            self.clear_logic_profile()
            self._logic_profile = profile
            if profile:
                profile = self._bot.get_logic_profile(profile)(self._bot, self)
                if hasattr(profile, "on_personal_message") and callable(getattr(profile, "on_personal_message")):
                    self.on_personal_message(profile.on_personal_message)
                if hasattr(profile, "on_join") and callable(getattr(profile, "on_join")):
                    self.on_join(profile.on_join)
                if hasattr(profile, "on_part") and callable(getattr(profile, "on_part")):
                    self.on_part(profile.on_part)
                if hasattr(profile, "on_message") and callable(getattr(profile, "on_message")):
                    self.on_message(profile.on_message)
            return profile

    def get_logic_profile(self):
        return self._logic_profile

    def get_attributes(self):
        return {
            "users": self._users,
            "messages": self._message_log,
            "logic_profile": self._logic_profile,
            "commands": self._commands,
            "command_descriptions": {command: self._commands[command]["description"] for command in self._commands},
            "broadcasts": self._bot.get_broadcast_controller().get_broadcasts(self._channel)
        }

    def import_attributes(self, data):
        for broadcast in self._bot.get_broadcast_controller().get_broadcasts(self._channel):
            self._bot.get_broadcast_controller().del_broadcast(broadcast["id"])
        for broadcast in data["broadcasts"]:
            self._bot.get_broadcast_controller().add_broadcast(broadcast["channel"], broadcast["message"], broadcast["secs"])

    def get_logic(self):
        return {"on_message": self.__on_message_method, "on_personal_message": self.__on_personal_message_method, "on_join": self.__on_join_method, "on_part": self.__on_part_method}

    def clear_logic_profile(self):
        self._logic_profile = ""
        self.clear_logic()
        self.clear_commands()
        if self.is_game():
            self.set_custom_config("")

    def clear_commands(self):
        if self.is_game():
            self._commands = {
                "!info": {
                "response": "built with [https://github.com/jramseygreen/osu_bot_framework-v3 osu_bot_framework v3] | [https://osu.ppy.sh/u/qqzzy Developer]",
                "description": "built with osu_bot_framework v3"
                },
            "!config": {
                "response": self.common_commands.config_link,
                "description": "Returns a link to the game rom configuration page"}
            }
        else:
            self._commands = {}

    # clear all on_event_methods
    def clear_logic(self):
        self.on_personal_message(None)
        self.on_join(None)
        self.on_part(None)
        self.on_message(None)

    def has_users(self):
        return self._users != []

    def has_user(self, username):
        return username.replace(" ", "_") in self.get_formatted_users()

    def new_vote_manager(self, method):
        return Vote(self._bot, self, method)

    def del_command(self, command):
        if command in self._commands:
            del self._commands[command]

    def get_commands(self):
        return self._commands

    def has_command(self, command):
        return command in self._commands

    def get_command(self, command):
        if command in self._commands:
            return self._commands["command"]