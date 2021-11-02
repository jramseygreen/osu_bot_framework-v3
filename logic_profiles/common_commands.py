class CommonCommands:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.add_command("!config", self.on_config, "returns a url to the room config")

    def on_config(self, message):
        self.channel.send_message("The configuration of the game room and available commands can be viewed [" + self.channel.get_config_link() + " here]")