class CommonCommands:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel

    def config_link(self, message):
        self.channel.send_message("The configuration of the game room and available commands can be viewed [" + self.channel.get_config_link() + " here]")

    def randmap(self, message):
        if self.channel.get_formatted_host() == message["username"] or message["username"] in self.channel.get_formatted_referees():
            query = message["content"].replace("!randmap", "").strip()
            if query == "":
                self.channel.send_message("Searching for beatmap...")
            else:
                self.channel.send_message("Searching for '" + query + "'...")

            beatmap = self.bot.chimu.fetch_random_beatmap(self.channel, query=query)
            if beatmap:
                self.channel.change_beatmap(beatmap["BeatmapId"])
            else:
                self.channel.send_message("No beatmaps found!")


    def altlink(self, message):
        self.channel.send_message("An alternate download link is available [" + self.bot.chimu.fetch_download_link(self.channel.get_beatmap()["id"]) + " here]")