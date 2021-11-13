import time


class HighRollers:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self.rolls = {}

    def on_match_finish(self):
        self.rolls = {}
        self.channel.send_message("You have 15sec to !roll for host!")
        time.sleep(10)
        for i in range(5, 0, -1):
            self.channel.send_message("Rolling concludes in " + str(i))
            time.sleep(1)
        if self.rolls:
            rolls = sorted(self.rolls, key=self.rolls.get, reverse=True)
            self.channel.set_host(self.bot.format_username(rolls[0]))
        elif self.channel.has_users():
            self.channel.set_host(self.channel.get_formatted_users()[0])

    def on_message(self, message):
        if message["username"] == "BanchoBot":
            user = message["content"][:message["content"].find("rolls")].strip()
            if user not in self.rolls:
                points = int(message["content"].replace(user + " rolls ", "").split(" ", 1)[0])
                self.rolls[user] = points