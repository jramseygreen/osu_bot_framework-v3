import math
import threading


class Vote:
    def __init__(self, bot, channel, method):
        self.bot = bot
        self.channel = channel
        self.method = method
        self.threshold = None
        self.results = {}
        self.in_progress = False

        self.__on_join_method = None
        self.__on_part_method = None

    def start(self, threshold=None):
        self.results = {}
        self.__on_join_method = self.channel.get_logic()["on_join"]
        self.__on_part_method = self.channel.get_logic()["on_part"]
        if not threshold:
            self.channel.on_join(self.__on_join)
            self.channel.on_part(self.__on_part)
            threshold = math.floor(len(self.channel.get_users()) / 2) + 1
        self.threshold = threshold
        self.in_progress = True

    def stop(self):
        if self.__on_join == self.channel.get_logic()["on_join"]:
            self.channel.on_join(self.__on_join_method)
        if self.__on_part == self.channel.get_logic()["on_part"]:
            self.channel.on_part(self.__on_part_method)
        self.in_progress = False

    def cast_ballot(self, username, choice=""):
        if not self.get_ballot(username) and self.in_progress:
            self.results[username] = choice
            # if any vote choice is past the threshold
            if self.results and any([list(self.results.values()).count(x) >= self.threshold for x in set(self.results.values())]):
                self.stop()
                x = threading.Thread(target=self.method, args=(self,))
                x.start()
                while x.is_alive():
                    pass
                self.threshold = None

    def get_results(self):
        return self.results

    def get_ballot(self, username):
        for user in self.results:
            if user.replace(" ", "_") == username.replace(" ", "_"):
                return self.results[user]

    def get_majority_vote(self):
        if self.results:
            return max(set(self.results.values()), key=list(self.results.values()).count)

    def get_threshold(self):
        return self.threshold

    def is_in_progress(self):
        return self.in_progress

    def __on_join(self, username):
        self.threshold = math.floor(len(self.channel.get_users()) / 2) + 1
        self.__on_join_method(username)

    def __on_part(self, username):
        self.threshold = math.floor(len(self.channel.get_users()) / 2) + 1
        if self.get_ballot(username) is not None:
            del self.results[username]
        # if any vote choice is past the threshold
        if self.results and any([list(self.results.values()).count(x) >= self.threshold for x in set(self.results.values())]):
            self.stop()
            x = threading.Thread(target=(self.method), args=(self,))
            x.start()
            while x.is_alive():
                pass
            self.threshold = None
        self.__on_part_method(username)
