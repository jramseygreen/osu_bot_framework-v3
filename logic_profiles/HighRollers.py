import random
import time


class HighRollers:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel

        self.roll_time = 30
        self.rolls = {}
        self.rolls_in_progress = False

        channel.set_command("!randmap", self.channel.common_commands.randmap, "Searches for a random map matching the room configuration")
        channel.set_command("!fight", self.channel.common_commands.fight, "Fight another user! e.g. '!fight peppy'. Victories stack.")
        channel.set_command("R̲e̲f̲e̲r̲e̲e̲ C̲o̲m̲m̲a̲n̲d̲s̲", "")
        channel.set_command("*roll_time", self.set_roll_time, "Set the rolling period in seconds if you are a referee. e.g. '*roll_time 60'")
        channel.set_custom_config("At the end of each match, !roll to decide the next host!\nThe current rolling time is: " + str(self.roll_time) + " seconds\n")

    def on_join(self, username):
        if self.channel.get_users() == [username]:
            self.rolls = {}
            self.rolls_in_progress = False
            self.channel.set_host(username)

    def on_part(self, username):
        if username in self.rolls:
            del self.rolls[username]
        if self.channel.is_host(username):
            self.on_clear_host()

    def on_match_finish(self):
        self.rolls = {}
        self.rolls_in_progress = True
        self.channel.clear_host()

    def on_match_abort(self):
        self.on_match_finish()

    def on_message(self, message):
        if message["username"] == "BanchoBot" and " rolls " in message["content"] and self.rolls_in_progress:
            user = message["content"][:message["content"].find("rolls")].strip()
            if user not in self.rolls:
                points = int(message["content"].replace(user + " rolls ", "").split(" ", 1)[0])
                if points <= 100:
                    self.rolls[user] = points
                else:
                    self.channel.send_message(user + " you may only type '!roll'")
            else:
                self.channel.send_message(user + " only your first !roll counts!")

    def on_clear_host(self):
        self.channel.send_message("You have " + str(self.roll_time) + " seconds to !roll for host...")
        for i in reversed(range(self.roll_time)):
            time.sleep(1)
            if i == 9:
                self.channel.send_message("rolling concludes in 10 seconds...")
            if i < 5:
                self.channel.send_message("rolling concludes in " + str(i + 1))
            if not self.channel.has_users():
                self.rolls_in_progress = False
                return
            if len(self.rolls) == len(self.channel.get_users()):
                break

        self.rolls_in_progress = False
        if self.rolls:
            username = max(self.rolls, key=self.rolls.get)
            self.channel.send_message(username + " took the host with " + str(self.rolls[username]) + " points rolled!")
            self.channel.set_host(username)
        else:
            self.channel.send_message("Nobody rolled! Picking random host...")
            self.channel.set_host(random.choice(self.channel.get_users()))

    def set_roll_time(self, message):
        if self.channel.has_referee(message["username"]):
            args = message["content"].split(" ")
            if len(args) == 2 and args[1].isnumeric():
                self.roll_time = int(args[1])
                self.channel.send_message("Set rolling time to " + args[1] + " seconds")
                self.channel.set_custom_config("At the end of each match, !roll to decide the next host!\nThe current rolling time is: " + str(self.roll_time) + " seconds\n")
