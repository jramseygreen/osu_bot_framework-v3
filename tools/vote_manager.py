import inspect
import math
import threading
import time


class Vote:
    def __init__(self, bot, channel, method):
        self.bot = bot
        self.channel = channel
        self.method = method
        self.threshold = None
        self.results = {}
        self.in_progress = False

        self.choices = []

        self.__on_join_method = None
        self.__on_part_method = None

    def start(self, choices=[], threshold=None):
        if not self.__on_join_method:
            self.__on_join_method = self.channel.get_logic()["on_join"]
        if not self.__on_part_method:
            self.__on_part_method = self.channel.get_logic()["on_part"]
        self.results = {}
        self.choices = choices

        if not threshold:
            self.channel.on_join(self.__on_join)
            self.channel.on_part(self.__on_part)
            threshold = math.floor(len(self.channel.get_users()) / 2) + 1
        self.threshold = threshold
        self.in_progress = True

    def stop(self):
        self.in_progress = False

    def cast_ballot(self, username, choice=""):
        success = False
        if username not in self.results and self.in_progress:
            if (self.choices and choice in self.choices) or not self.choices:
                success = True
                self.results[username] = choice
                # if any vote choice is past the threshold
                if self.results and len(self.results) >= self.threshold:
                    self.stop()
                    time.sleep(0.5)
                    if len(str(inspect.signature(self.method)).strip("()").split(", ")) == 1:
                        threading.Thread(target=self.method, args=(self,)).start()
                    else:
                        threading.Thread(target=self.method).start()

        return success

    def get_results(self):
        return self.results

    def get_ballot(self, username):
        for user in self.results:
            if user.replace(" ", "_") == username.replace(" ", "_"):
                return self.results[user]

    # returns the most voted for option
    def get_majority_vote(self):
        if self.results:
            return max(set(self.results.values()), key=list(self.results.values()).count)

    def get_threshold(self):
        return self.threshold

    def is_in_progress(self):
        return self.in_progress

    def __on_join(self, slot, username):
        if self.in_progress:
            self.threshold = math.floor(len(self.channel.get_users()) / 2) + 1

        argnum = len(str(inspect.signature(self.__on_join_method)).strip("()").split(", "))
        if argnum == 2:
            threading.Thread(target=self.__on_join_method, args=(slot, username,)).start()
        elif argnum == 1:
            threading.Thread(target=self.__on_join_method, args=(username,)).start()
        else:
            threading.Thread(target=self.__on_join_method).start()

    def __on_part(self, slot, username):
        if self.in_progress:
            self.threshold = math.floor(len(self.channel.get_users()) / 2) + 1
            if self.get_ballot(username) is not None:
                del self.results[username]
            # if any vote choice is past the threshold
            if self.results and len(self.results) >= self.threshold:
                self.stop()
                time.sleep(0.5)
                if len(str(inspect.signature(self.method)).strip("()").split(", ")) == 1:
                    threading.Thread(target=self.method, args=(self,)).start()
                else:
                    threading.Thread(target=self.method).start()

        argnum = len(str(inspect.signature(self.__on_part_method)).strip("()").split(", "))
        if argnum == 2:
            threading.Thread(target=self.__on_part_method, args=(slot, username,)).start()
        elif argnum == 1:
            threading.Thread(target=self.__on_part_method, args=(username,)).start()
        else:
            threading.Thread(target=self.__on_part_method).start()
