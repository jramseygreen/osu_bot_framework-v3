class KingOfTheHill:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.set_beatmap_checker(True)
        self.scores = []
        channel.set_command("!skip", self.skip, "Skip your turn if you are host.")

    def skip(self, message):
        if self.channel.get_formatted_host() == message["username"]:
            if self.scores:
                self.scores.append(self.scores.pop(0))
                self.channel.set_host(self.scores[0]["username"])
            elif self.channel.has_users():
                self.channel.get_users().append(self.channel.get_users().pop(0))
                self.channel.set_host(self.channel.get_users()[0])

    def on_join(self, username, slot):
        if self.channel.get_users() == [username]:
            self.channel.set_host(username)

    def on_part(self, username):
        if self.channel.get_host() == username:
            self.scores.pop(0)
            if self.channel.has_users():
                if self.scores:
                    self.channel.set_host(self.scores[0]["username"])
                else:
                    self.channel.set_host(self.channel.get_users()[0])

    def on_match_finish(self):
        self.scores = self.channel.get_ordered_scores()
        match = self.channel.get_match_data()
        key = "max_combo"
        if "score" in match["scoring_type"]:
            key = "score"
        elif "accuracy" == match["scoring_type"]:
            key = "accuracy"
        self.channel.send_message(self.scores[0]["username"] + " wins with " + match["scoring_type"].replace("v2", "") + ": " + str(self.scores[0][key]))
        self.channel.set_host(self.scores[0]["username"])

    def on_match_abort(self):
        self.on_match_finish()