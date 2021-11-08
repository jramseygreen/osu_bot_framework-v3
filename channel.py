import copy
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
        self.verbose = verbose
        self._logic_profile = ""
        self.common_commands = CommonCommands(bot, self)

        # on_event methods
        self.__on_personal_message_method = None
        self.__on_join_method = None
        self.__on_part_method = None
        self.__on_message_method = None

    def add_user(self, username):
        if username.replace(" ", "_") not in self.get_formatted_users():
            self._users.append(username)
        if self.__on_join_method:
            if self.is_game():
                slot = self.get_slot_num(username)
                argnum = len(str(inspect.signature(self.__on_join_method)).strip("()").split(", "))
                if argnum == 2:
                    threading.Thread(target=self.__on_join_method, args=(slot, username,)).start()
                elif argnum == 1:
                    threading.Thread(target=self.__on_join_method, args=(username,)).start()
                else:
                    threading.Thread(target=self.__on_join_method).start()

    def del_user(self, username):
        slot = None
        if self.is_game():
            slot = self.get_slot_num(username)
        if username.replace(" ", "_") in self.get_formatted_users():
            del self._users[self.get_formatted_users().index(username.replace(" ", "_"))]
        if self.__on_part_method:
            argnum = len(str(inspect.signature(self.__on_part_method)).strip("()").split(", "))
            if argnum == 2:
                threading.Thread(target=self.__on_part_method, args=(slot, username,)).start()
            elif argnum == 1:
                threading.Thread(target=self.__on_part_method, args=(username,)).start()
            else:
                threading.Thread(target=self.__on_part_method).start()

    def process_message(self, message):
        if len(self._message_log) == self._message_log_length:
            self._message_log = self._message_log[1:]
        self._message_log.append(message)
        if self.__on_message_method:
            if len(str(inspect.signature(self.__on_message_method)).strip("()").split(", ")) == 1:
                threading.Thread(target=self.__on_message_method, args=(message,)).start()
            else:
                threading.Thread(target=self.__on_message_method).start()

    def send_message(self, message):
        self._bot.get_sock().sendall(("PRIVMSG " + self._channel + " :" + str(message) + "\n").encode())
        if len(self._message_log) == self._message_log_length:
            self._message_log = self._message_log[1:]
        self._message_log.append({"username": self._bot.get_username().replace(" ", "_"), "channel": self._channel, "content": message})
        if self.verbose or self._bot.logging:
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
        self.clear_logic_profile()
        self._logic_profile = profile
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
        return {"users": self._users, "messages": self._message_log}

    def import_attributes(self, data):
        pass

    def get_logic(self):
        return {"on_message": self.__on_message_method, "on_personal_message": self.__on_personal_message_method, "on_join": self.__on_join_method, "on_part": self.__on_part_method}

    def clear_logic_profile(self):
        self._logic_profile = ""
        self.clear_logic()

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

    def hold_vote(self, method):
        return Vote(self._bot, self, method)