import time


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# contains common command responses
class CommonCommands:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self.played = []

    def config_link(self, message):
        self.channel.send_message("The configuration of the game room and available commands can be viewed [" + self.channel.get_config_link() + " here]")

    def randmap(self, message):
        command = message["content"].split(" ", 1)[0]
        if self.channel.get_formatted_host() == message["username"] or self.channel.has_referee(message["username"]):
            query = message["content"].replace(command, "", 1).strip()
            if query == "":
                self.channel.send_message("Searching for beatmap...")
            else:
                self.channel.send_message("Searching for '" + query + "'...")

            beatmap = self.bot.chimu.fetch_random_beatmap(self.channel, query=query)
            while beatmap["BeatmapId"] in self.played:
                beatmap = self.bot.chimu.fetch_random_beatmap(self.channel, query=query)
            if len(self.played) >= 50:
                self.played.pop(0)
            self.played.append(beatmap["BeatmapId"])
            if beatmap:
                self.channel.change_beatmap(beatmap["BeatmapId"])
            else:
                self.channel.send_message("No beatmaps found!")
        else:
            self.channel.send_message("This command is only available to the host or referees.")

    def altlink(self, message):
        self.channel.send_message("An alternate download link is available [" + self.bot.chimu.fetch_download_link(self.channel.get_beatmap()["id"]) + " here]")

    def ar_range(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 2:
                if all([is_number(arg) for arg in args]):
                    self.channel.set_ar_range((float(args[0]), float(args[1])))
                else:
                    self.channel.send_message(message["username"] + " you can only send numbers with this command.")
                    return
            else:
                self.channel.send_message(message["username"] + " you must send 2 arguments with this command.")
                return
            self.channel.send_message("The ar range was set to " + str(self.channel.get_ar_range()))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def od_range(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 2:
                if all([is_number(arg) for arg in args]):
                    self.channel.set_od_range((float(args[0]), float(args[1])))
                else:
                    self.channel.send_message(message["username"] + " you can only send numbers with this command.")
                    return
            else:
                self.channel.send_message(message["username"] + " you must send 2 arguments with this command.")
                return
            self.channel.send_message("The od range was set to " + str(self.channel.get_od_range()))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def hp_range(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 2:
                if all([is_number(arg) for arg in args]):
                    self.channel.set_hp_range((float(args[0]), float(args[1])))
                else:
                    self.channel.send_message(message["username"] + " you can only send numbers with this command.")
                    return
            else:
                self.channel.send_message(message["username"] + " you must send 2 arguments with this command.")
                return
            self.channel.send_message("The hp range was set to " + str(self.channel.get_hp_range()))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
            
    def cs_range(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 2:
                if all([is_number(arg) for arg in args]):
                    self.channel.set_cs_range((float(args[0]), float(args[1])))
                else:
                    self.channel.send_message(message["username"] + " you can only send numbers with this command.")
                    return
            else:
                self.channel.send_message(message["username"] + " you must send 2 arguments with this command.")
                return
            self.channel.send_message("The cs range was set to " + str(self.channel.get_cs_range()))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
            
    def bpm_range(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 2:
                if all([is_number(arg) for arg in args]):
                    self.channel.set_bpm_range((float(args[0]), float(args[1])))
                else:
                    self.channel.send_message(message["username"] + " you can only send numbers with this command.")
                    return
            else:
                self.channel.send_message(message["username"] + " you must send 2 arguments with this command.")
                return
            self.channel.send_message("The bpm range was set to " + str(self.channel.get_bpm_range()))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
            
    def diff_range(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 2:
                if all([is_number(arg) for arg in args]):
                    self.channel.set_diff_range((float(args[0]), float(args[1])))
                else:
                    self.channel.send_message(message["username"] + " you can only send numbers with this command.")
                    return
            else:
                self.channel.send_message(message["username"] + " you must send 2 arguments with this command.")
                return
            self.channel.send_message("The difficulty range was set to " + str(self.channel.get_diff_range()))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
            
    def length_range(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 2:
                if all([arg.isnumeric() for arg in args]):
                    self.channel.set_length_range((int(args[0]), int(args[1])))
                else:
                    self.channel.send_message(message["username"] + " you can only send integers with this command.")
                    return
            else:
                self.channel.send_message(message["username"] + " you must send 2 arguments with this command.")
                return
            length_range = []
            if int(args[1]) < 0:
                length_range = [str(int(args[0]) // 60) + "min, " + str(int(args[0]) % 60) + "sec", "unlimited"]
            else:
                length_range = [str(int(x) // 60) + "min, " + str(int(x) % 60) + "sec" for x in self.channel.get_length_range()]
            self.channel.send_message("The length range was set to " + str(self.channel.get_length_range()) + " - " + str(length_range))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
            
    def map_status(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if args:
                self.channel.set_map_status(args)
            else:
                self.channel.set_map_status("any")
            self.channel.send_message("The map status was set to " + str(self.channel.get_map_status()))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
            
    def mods(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if args:
                self.channel.set_mods(args)
            else:
                self.channel.set_mods("any")
            self.channel.send_message("Allowed mods set to " + str(self.channel.get_mods()))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
            
    def scoring_type(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 1:
                self.channel.set_scoring_type(args[0])
            elif not args:
                self.channel.set_scoring_type("any")
            else:
                self.channel.send_message(message["username"] + " you must send 1 argument with this command.")
                return
            self.channel.send_message("Allowed scoring type set to: " + self.channel.get_scoring_type())
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
            
    def team_type(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 1:
                self.channel.set_team_type(args[0])
            elif not args:
                self.channel.set_team_type("any")
            else:
                self.channel.send_message(message["username"] + " you must send 1 argument with this command.")
                return
            self.channel.send_message("Allowed team type set to: " + self.channel.get_team_type())
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
            
    def game_mode(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 1:
                self.channel.set_game_mode(args[0])
            elif not args:
                self.channel.set_game_mode("any")
            else:
                self.channel.send_message(message["username"] + " you must send 1 argument with this command.")
                return
            self.channel.send_message("Allowed game mode set to: " + self.channel.get_game_mode())
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def welcome_message(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            msg = message["content"].replace(command, "", 1).strip()
            if msg:
                self.channel.set_welcome_message(msg)
            else:
                self.channel.set_welcome_message("")
            self.channel.send_message("Set the welcome message to " + msg)
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def add_broadcast(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) > 1:
                if is_number(args[0]):
                   id = self.channel.add_broadcast(" ".join(args[1:]), args[0])
                   self.channel.send_message("Broadcast id: " + str(id) + " started")
            else:
                self.channel.send_message(message["username"] + " you must send a time in seconds and a message to broadcast.")
                return
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")
    
    def del_broadcast(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 1:
                if self.bot.has_broadcast_id(args[0]):
                    if self.bot.get_broadcast(args[0]) in self.bot.get_broadcasts(self.channel.get_channel()):
                        self.bot.del_broadcast(args[0])
                    else:
                        self.channel.send_message(message["username"] + " broadcast id does not belong to this channel.")
                        return
                else:
                    self.channel.send_message(message["username"] + " broadcast id not recognised.")
                    return
                self.channel.send_message("Broadcast id: " + args[0] + " stopped")
            else:
                self.channel.send_message(message["username"] + " you must send 1 argument with this command.")
                return
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def add_beatmap_creator_whitelist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            creator = message["content"].replace(command, "", 1).strip()
            if creator:
                self.channel.add_beatmap_creator_whitelist(creator)
                self.channel.send_message("'" + creator + "'" + " added to the creator whitelist")

    def del_beatmap_creator_whitelist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            creator = message["content"].replace(command, "", 1).strip()
            if creator:
                self.channel.del_beatmap_creator_whitelist(creator)
                self.channel.send_message("'" + creator + "'" + " removed from the creator whitelist")

    def add_beatmap_creator_blacklist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            creator = message["content"].replace(command, "", 1).strip()
            if creator:
                self.channel.add_beatmap_creator_blacklist(creator)
                self.channel.send_message("'" + creator + "'" + " added to the creator blacklist")

    def del_beatmap_creator_blacklist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            creator = message["content"].replace(command, "", 1).strip()
            if creator:
                self.channel.del_beatmap_creator_blacklist(creator)
                self.channel.send_message("'" + creator + "'" + " removed from the creator blacklist")

    def add_artist_whitelist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            artist = message["content"].replace(command, "", 1).strip()
            if artist:
                self.channel.add_artist_whitelist(artist)
                self.channel.send_message("'" + artist + "'" + " added to the artist whitelist")

    def del_artist_whitelist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            artist = message["content"].replace(command, "", 1).strip()
            if artist:
                self.channel.del_artist_whitelist(artist)
                self.channel.send_message("'" + artist + "'" + " removed from the artist whitelist")

    def add_artist_blacklist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            artist = message["content"].replace(command, "", 1).strip()
            if artist:
                self.channel.add_artist_blacklist(artist)
                self.channel.send_message("'" + artist + "'" + " added to the artist blacklist")

    def del_artist_blacklist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            artist = message["content"].replace(command, "", 1).strip()
            if artist:
                self.channel.del_artist_blacklist(artist)
                self.channel.send_message("'" + artist + "'" + " removed from the artist blacklist")

    def implement_logic_profile(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if len(args) == 1:
                if args[0] in self.bot.get_logic_profiles():
                    self.channel.implement_logic_profile(args[0])
                else:
                    self.channel.send_message(message["username"] + " this logic profile does not exist.")
                    return
                self.channel.send_message("Command '" + command + "' executed successfully")
            else:
                self.channel.send_message(message["username"] + " you must send 1 argument with this command.")
                return
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def get_logic_profiles(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.send_message("Available logic profiles: " + ", ".join(self.bot.get_logic_profiles().keys()))
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def enable_beatmap_checker(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            self.channel.set_beatmap_checker(True)
            self.channel.send_message("Command '" + command + "' executed successfully")
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def disable_beatmap_checker(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            self.channel.set_beatmap_checker(False)
            self.channel.send_message("Command '" + command + "' executed successfully")
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def start_timer(self, message):
        if message["username"] == self.channel.get_formatted_host() or self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if args and args[0].isnumeric():
                self.channel.start_match(args[0])
            else:
                self.channel.start_match()

    def abort_start_timer(self, message):
        if message["username"] == self.channel.get_formatted_host() or self.channel.has_referee(message["username"]):
            self.channel.abort_start_timer()
            self.channel.send_message("Aborted the match start timer")

    # todo
    def topdiff(self, message):
        beatmapset = self.bot.fetch_beatmapset(self.channel.get_beatmap["id"])
        for beatmap in reversed(beatmapset["beatmaps"]):
            if self.channel.get_ar_range()[0] < beatmap["ar"] < self.channel.get_ar_range()[1]:
                self.channel.change_beatmap(beatmap["id"])
