import copy
import threading


class Channel:
    def __init__(self, bot, channel, verbose):
        self._bot = bot
        self._channel = channel
        self._message_log = []
        self._message_log_length = 50
        self._users = []
        self.verbose = verbose

        # on_event methods
        self.__on_personal_message_method = None
        self.__on_join_method = None
        self.__on_part_method = None
        self.__on_message_method = None

    def add_user(self, username):
        if username not in self._users:
            self._users.append(username)
        if self.__on_join_method:
            threading.Thread(target=self.__on_join_method, args=(username,)).start()

    def del_user(self, username):
        if username in self._users:
            self._users.remove(username)
        if self.__on_part_method:
            threading.Thread(target=self.__on_part_method, args=(username,)).start()

    def process_message(self, message):
        if len(self._message_log) == self._message_log_length:
            self._message_log = self._message_log[1:]
        self._message_log.append(message)
        if self.__on_message_method:
            threading.Thread(target=self.__on_message_method, args=(message,)).start()

    def send_message(self, message):
        self._bot.get_sock().sendall(("PRIVMSG " + self._channel + " :" + str(message) + "\n").encode())
        if self.verbose:
            print("-- sent message to " + self._channel + ": '" + str(message) + "' --")

    def is_game(self):
        return self._channel[:4] == "#mp_"

    def get_channel(self):
        return self._channel

    def get_users(self):
        return self._users

    def set_message_log_length(self, length):
        self._message_log_length = length

    def get_message_log(self, username=""):
        if username:
            message_log = []
            for message in copy.deepcopy(self._message_log):
                if message["username"] == username:
                    message_log.append(message)
            return message_log
        return copy.deepcopy(self._message_log)

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
        profile = self._bot.get_logic_profile(profile)(self._bot, self)
        if hasattr(profile, "on_personal_message") and callable(getattr(profile, "on_personal_message")):
            self.on_personal_message(profile.on_personal_message)
        if hasattr(profile, "on_join") and callable(getattr(profile, "on_join")):
            self.on_join(profile.on_join)
        if hasattr(profile, "on_part") and callable(getattr(profile, "on_part")):
            self.on_part(profile.on_part)
        if hasattr(profile, "on_message") and callable(getattr(profile, "on_message")):
            self.on_message(profile.on_message)

    def get_attributes(self):
        return {"users": self._users, "messages": self._message_log}

    def get_logic(self):
        return {"on_message": self.__on_message_method, "on_personal_message": self.__on_personal_message_method, "on_join": self.__on_join_method, "on_part": self.__on_part_method}