class KingOfTheHill:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.set_beatmap_checker(True)
        channel.maintain_password(True)
        channel.maintain_size(True)
        channel.set_custom_config("King Of The Hill:\n\nSee how good you really are! The bot will automatically give host to the top scoring player.\n\n")
        self.scores = []
        channel.set_command("!config", channel.common_commands.config_link, "Returns a link to the game room configuration page")
        channel.set_command("!randmap", channel.common_commands.randmap, "When host or referee, searches for a random beatmap matching the room's limits and ranges")
        channel.set_command("!altlink", channel.common_commands.altlink, "Returns an alternate link for the current beatmap from BeatConnect.io")
        channel.set_command("!topdiff", channel.common_commands.topdiff, "When host, upgrades the beatmap to the highest difficulty within the room limits and ranges")
        channel.set_command("!start", channel.common_commands.start_timer, "When host or referee, starts the game with optional countdown timer")
        channel.set_command("!aborttimer", channel.common_commands.abort_start_timer, "When host or referee, aborts start timer")
        channel.set_command("!update", channel.common_commands.update_beatmap, "Updates current beatmap")
        channel.set_command("!skip", self.skip, "when you are the host, transfers host to the next highest scoring player")
        channel.set_command("R̲e̲f̲e̲r̲e̲e̲ C̲o̲m̲m̲a̲n̲d̲s̲", "")
        channel.set_command("*implement", channel.common_commands.implement_logic_profile, "Implements a logic profile")
        channel.set_command("*logic_profiles", channel.common_commands.get_logic_profiles, "Shows available logic profiles")
        channel.set_command("*scoring_type", channel.common_commands.scoring_type, "Sets the allowed scoring mode for the room. e.g. *scoring_type score")

    def skip(self, message):
        if self.channel.get_formatted_host() == message["username"]:
            if self.scores:
                self.scores.append(self.scores.pop(0))
                self.channel.set_host(self.scores[0]["username"])
            elif self.channel.has_users():
                self.channel.get_users().append(self.channel.get_users().pop(0))
                self.channel.set_host(self.channel.get_users()[0])

    def on_join(self, username):
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
        self.channel.send_message(self.scores[0]["username"] + " wins with " + match["scoring_type"].replace("v2", "") + ": " + str(round(self.scores[0][key] * 10) / 10))
        self.channel.set_host(self.scores[0]["username"])

    def on_match_abort(self):
        self.on_match_finish()