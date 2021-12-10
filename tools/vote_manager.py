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
        self.is_in_progress = False

        self.choices = []
        self.cooldown = False

        self.__on_join_method = None
        self.__on_part_method = None

    def hold_vote(self, choices=[], threshold=None):
        if not self.is_in_progress:
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
            self.is_in_progress = True

    def stop(self):
        self.is_in_progress = False
        x = threading.Thread(target=self.__cooldown_timer)
        x.setDaemon(True)
        x.start()

    def __cooldown_timer(self):
        self.cooldown = True
        time.sleep(5)
        self.cooldown = False

    def restart(self, threshold=None):
        self.stop()
        self.hold_vote(self.choices, threshold)

    def __trigger(self):
        if not self.cooldown and (self.get_ballot_number() >= len(self.channel.get_users()) or (self.results and any([list(self.results.values()).count(x) >= self.threshold for x in set(self.results.values())]))):
            x = None
            if str(inspect.signature(self.method)).strip("()").split(", ") != [""]:
                x = threading.Thread(target=self.method, args=(self,))
            else:
                x = threading.Thread(target=self.method)
            x.setDaemon(True)
            x.start()
            self.stop()

    def cast_ballot(self, username, choice=""):
        success = False
        if not self.cooldown:
            if not self.is_in_progress:
                self.hold_vote()
            if username not in self.results and self.is_in_progress:
                if (self.choices and choice in self.choices) or not self.choices:
                    success = True
                    self.results[username] = choice
                    msg = username + " voted: " + choice + " | " + str(self.get_ballot_number()) + " / " + str(self.threshold) + " votes needed"
                    if self.choices:
                        msg += " - "
                        for c in self.choices:
                            msg += " '" + c + "': "
                            msg += str(len(self.get_results(c))) + " votes |"
                    self.channel.send_message(msg.strip("|"))

                    # if any vote choice is past the threshold
                    self.__trigger()

        return success

    def get_choices(self):
        return self.choices

    def get_results(self, choice=None):
        results = self.results
        if choice:
            results = {username: self.results[username] for username in self.results if self.results[username] == choice}
        return results

    def get_users(self, choice=""):
        results = []
        for username in self.results:
            if self.results[username] == choice:
                results.append(username)
        return results

    def get_ballot(self, username):
        for user in self.results:
            if user.replace(" ", "_") == username.replace(" ", "_"):
                return self.results[user]

    def get_ballot_number(self):
        return len(self.results)

    # returns the most voted for option
    def get_majority_vote(self):
        if self.results:
            return max(set(self.results.values()), key=list(self.results.values()).count)

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.__trigger()

    def in_progress(self):
        return self.is_in_progress

    def __on_join(self, username, slot):
        if self.is_in_progress:
            self.threshold = math.floor(len(self.channel.get_users()) / 2) + 1

        if self.__on_join_method:
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

    def __on_part(self, username, slot):
        if self.is_in_progress:
            self.threshold = math.floor(len(self.channel.get_users()) / 2) + 1
            if self.get_ballot(username) is not None:
                del self.results[username]
            # if any vote choice is past the threshold
            self.__trigger()

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