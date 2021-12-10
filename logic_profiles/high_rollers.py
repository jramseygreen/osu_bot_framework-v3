import time


class HighRollers:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self.rolls = {}
        self.validated = []
        channel.set_command("!roll", self.roll)

    def on_match_finish(self):
        self.rolls = {}
        self.validated = []
        self.channel.send_message("You have 30sec to !roll for host!")
        time.sleep(25)
        for i in range(5, 0, -1):
            self.channel.send_message("Rolling concludes in " + str(i))
            time.sleep(1)
        if self.rolls:
            rolls = sorted(self.rolls, key=self.rolls.get, reverse=True)
            self.channel.set_host(self.bot.format_username(rolls[0]))
        elif self.channel.has_users():
            self.channel.set_host(self.channel.get_formatted_users()[0])

    def on_match_abort(self):
        self.on_match_finish()

    def on_join(self, username):
        if self.channel.get_users() == [username]:
            self.channel.set_host(username)

    def on_message(self, message):
        if message["username"] == "BanchoBot" and " rolls " in message["content"]:
            user = self.bot.format_username(message["content"][:message["content"].find("rolls")].strip())
            if user not in self.rolls and user in self.validated:
                points = int(message["content"].replace(user + " rolls ", "").split(" ", 1)[0])
                self.rolls[user] = points

    def roll(self, message):
        if message["content"] == "!roll":
            if message["username"] not in self.validated:
                self.validated.append(message["username"])
        else:
            self.channel.send_message(message["username"] + " you may only type '!roll'")