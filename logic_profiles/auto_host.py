class AutoHost:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.set_command("!add", self.on_add, "Adds a beatmap to the queue")
        channel.set_command("!q", self.show_queue, "Shows the queue of beatmaps")
        channel.set_command("!queue", self.show_queue, "Shows the queue of beatmaps")
        channel.start_on_players_ready(True)

        self.queue = []
        self.requested = []

    def on_add(self, message):
        beatmap = {}
        beatmapID = message["content"].split("/")[-1]
        if len(message["content"].replace("!add", "").strip()) == 1:
            beatmap = self.channel.fetch_beatmap(beatmapID)
        if self.channel.beatmap_checker_on():
            error = self.channel.check_beatmap(beatmap)
            if error:
                self.channel.send_message(message["username"] + " " + error["message"])
                return
        if message["username"] not in self.requested:
            self.queue.append(message["content"].split("/")[-1])
            self.requested.append(message["username"])
            self.channel.send_message(message["username"] + " added [https://osu.ppy.sh/b/" + str(beatmapID) + " https://osu.ppy.sh/b/" + str(beatmapID) + "]")
        else:
            self.channel.send_message("Sorry " + message["username"] + " you can only add one beatmap at a time!")

    def on_join(self, username, slot):
        if self.channel.get_users() == [username]:
            self.channel.clear_host()

    def on_match_finish(self):
        self.next_round()

    def on_match_abort(self):
        self.on_match_finish()

    def next_round(self):
        beatmapID = 22538
        if self.queue:
            beatmapID = self.queue.pop(0)
            self.requested.pop(0)
        else:
            beatmapID = self.bot.chimu.fetch_random_beatmap(self.channel)["BeatmapId"]
        self.channel.change_beatmap(beatmapID)

    def show_queue(self):
        text = "Beatmap queue:\n\n"
        for beatmapID in self.queue:
            text += "https://osu.ppy.sh/b/" + str(beatmapID) + "\n"
        self.channel.send_message("The current queue of beatmaps is available [" + self.bot.paste2_upload("beatmap queue for " + self.channel.get_channel(), text) + " here]")