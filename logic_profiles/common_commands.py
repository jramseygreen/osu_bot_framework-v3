class CommonCommands:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.add_command("!config", self.on_config, "returns a url to the room config")
        channel.add_command("!randmap", self.on_randmap, "returns a random map fitting the room limits & ranges. Optionally add a search term.")
        channel.add_command("!altlink", self.on_altlink, "returns an alternate download link for the current beatmap from chimu.moe")

    def on_config(self, message):
        self.channel.send_message("The configuration of the game room and available commands can be viewed [" + self.channel.get_config_link() + " here]")

    def on_randmap(self, message):
        if message["content"] == "!randmap":
            self.channel.send_message("Searching for beatmap...")
            beatmap = self.bot.chimu.fetch_random_beatmap(self.channel)
            if beatmap:
                self.channel.change_beatmap(beatmap["BeatmapId"])
            else:
                self.channel.send_message("No beatmaps found!")
        else:
            query = message["content"].replace("!randmap", "").strip()
            self.channel.send_message("Searching for '" + query + "'...")
            beatmap = self.bot.chimu.fetch_random_beatmap(self.channel, query=query)
            if beatmap:
                self.channel.change_beatmap(beatmap["BeatmapId"])
            else:
                self.channel.send_message("No beatmaps found!")

    def on_altlink(self, message):
        self.channel.send_message("An alternate download link is available [" + self.bot.chimu.fetch_download_link(self.channel.get_beatmap()["id"]) + " here]")