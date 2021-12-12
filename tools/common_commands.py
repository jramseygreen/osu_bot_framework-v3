import os
import random
import time

from GAME_ATTR import GAME_ATTR


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
        self.fights = {}

    def config_link(self, message):
        self.channel.send_message("The configuration of the game room and available commands can be viewed [" + self.channel.get_config_link() + " here]")

    def import_config(self, message):
        if self.channel.has_referee(message["username"]):
            if "paste2.org" in message["content"]:
                self.channel.import_config(message["content"].split(" ", 1)[1])
            else:
                self.channel.send_message(message["content"].split(" ", 1)[1] + " is not a valid configuration page")
        else:
            self.channel.send_message("This command is only available to referees.")

    def randmap(self, message):
        command = message["content"].split(" ", 1)[0]
        if self.channel.get_formatted_host() == message["username"] or self.channel.has_referee(message["username"]):
            query = message["content"].replace(command, "", 1).strip()
            offset = 0
            if query == "":
                self.channel.send_message("Searching for beatmap...")
            else:
                self.channel.send_message("Searching for '" + query + "'...")

            beatmap = self.bot.chimu.fetch_random_beatmap(self.channel, query=query, offset=offset)
            if beatmap:
                self.channel.change_beatmap(beatmap["BeatmapId"])
            else:
                self.channel.send_message("No beatmaps found!")
        else:
            self.channel.send_message("This command is only available to the host or referees.")

    def altlink(self, message):
        link = self.bot.chimu.fetch_download_link(self.channel.get_beatmap()["id"])
        if link:
            self.channel.send_message("An alternate download link is available [" + link + " here]")
        else:
            self.channel.send_message("Sorry chimu.moe doesn't store this beatmap!")

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
                if all([arg.lower() in GAME_ATTR for arg in args]):
                    self.channel.set_map_status(args)
                else:
                    self.channel.send_message("One or more unrecognised arguments!")
                    return
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
                if all([arg.upper() in GAME_ATTR for arg in args]):
                    self.channel.set_mods(args)
                else:
                    self.channel.send_message("One or more unrecognised arguments!")
                    return
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
                if args[0].lower() in GAME_ATTR:
                    self.channel.set_scoring_type(args[0])
                else:
                    self.channel.send_message("One or more unrecognised arguments!")
                    return
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
                if args[0].lower() in GAME_ATTR:
                    self.channel.set_team_type(args[0])
                else:
                    self.channel.send_message("One or more unrecognised arguments!")
                    return
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
                if args[0].lower() in GAME_ATTR:
                    self.channel.set_game_mode(args[0])
                else:
                    self.channel.send_message("One or more unrecognised arguments!")
                    return
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
                if creator.lower() not in self.channel.get_beatmap_creator_whitelist():
                    self.channel.add_beatmap_creator_whitelist(creator)
                    self.channel.send_message("'" + creator + "'" + " added to the creator whitelist")
                else:
                    self.channel.send_message("'" + creator + "' is already in the whitelist")

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
                if creator.lower() not in self.channel.get_beatmap_creator_blacklist():
                    self.channel.add_beatmap_creator_blacklist(creator)
                    self.channel.send_message("'" + creator + "'" + " added to the creator blacklist")
                else:
                    self.channel.send_message("'" + creator + "' is already in the blacklist")

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
                if artist.lower() not in self.channel.get_artist_whitelist():
                    self.channel.add_artist_whitelist(artist)
                    self.channel.send_message("'" + artist + "'" + " added to the artist whitelist")
                else:
                    self.channel.send_message("'" + artist + "' is already in the whitelist")

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
                if artist.lower() not in self.channel.get_artist_blacklist():
                    self.channel.add_artist_blacklist(artist)
                    self.channel.send_message("'" + artist + "'" + " added to the artist blacklist")
                else:
                    self.channel.send_message("'" + artist + "' is already in the blacklist")

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
                self.channel.send_message("Logic Profile: '" + args[0] + "' implemented successfully")
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
            self.channel.send_message("Enabled beatmap checker")
        else:
            self.channel.send_message("Sorry " + message["username"] + " that command is only for referees!")

    def disable_beatmap_checker(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            self.channel.set_beatmap_checker(False)
            self.channel.send_message("Disabled beatmap Checker")
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

    def enable_start_on_players_ready(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.start_on_players_ready(True)
            self.channel.send_message("Enabled starting automatically when all players are ready")

    def disable_start_on_players_ready(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.start_on_players_ready(False)
            self.channel.send_message("Disabled starting automatically when all players are ready")

    def set_auto_start_timer(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            args = message["content"].replace(command, "", 1).strip().split(" ")
            if is_number(args[0]):
                self.channel.set_autostart_timer(True, args[0])
                if self.channel.is_autostart_timer():
                    self.channel.send_message("Autostart timer set to " + args[0])
                else:
                    self.channel.send_message("Autostart timer disabled")

    def add_player_blacklist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            player = message["content"].replace(command, "", 1).strip()
            if player and player.replace(" ", "_") not in self.channel.get_formatted_player_blacklist():
                self.channel.add_player_blacklist(player)
                self.channel.kick_user(player)
                self.channel.send_message("'" + player + "' added to the blacklist")

    def del_player_blacklist(self, message):
        if self.channel.has_referee(message["username"]):
            command = message["content"].split(" ", 1)[0]
            player = message["content"].replace(command, "", 1).strip()
            if player and player.replace(" ", "_") in self.channel.get_formatted_player_blacklist():
                self.channel.del_player_blacklist(player)
                self.channel.send_message("'" + player + "' removed from the blacklist")

    def enable_maintain_title(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.maintain_title(True)
            self.channel.send_message("Enabled maintaining title")

    def disable_maintain_title(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.maintain_title(False)
            self.channel.send_message("Disabled maintaining title")

    def enable_maintain_password(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.maintain_password(True)
            self.channel.send_message("Enabled maintaining password")

    def disable_maintain_password(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.maintain_password(False)
            self.channel.send_message("Disabled maintaining password")

    def enable_maintain_size(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.maintain_size(True)
            self.channel.send_message("Enabled maintaining size")

    def disable_maintain_size(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.maintain_size(False)
            self.channel.send_message("Disabled maintaining size")

    def enable_auto_download(self, message):
        if message["username"] == self.bot.get_username():
            self.channel.auto_download(True, auto_open=True)
            self.channel.send_message("The bot will now download beatmaps automatically")
        else:
            self.channel.send_message("Sorry this command can only be used by the bot administrator!")

    def disable_auto_download(self, message):
        if message["username"] == self.bot.get_username():
            self.channel.auto_download(False)
            self.channel.send_message("Automatic beatmap download disabled")
        else:
            self.channel.send_message("Sorry this command can only be used by the bot administrator!")

    def topdiff(self, message):
        beatmapset = self.bot.fetch_beatmapset(self.channel.get_beatmap()["id"])
        if beatmapset:
            for beatmap in sorted(beatmapset["beatmaps"], key=lambda x: x["difficulty_rating"], reverse=True):
                error = None
                if self.channel.beatmap_checker_on():
                    error = self.channel.check_beatmap(beatmap)
                if not error or error["type"] == "unsubmitted":
                    self.channel.change_beatmap(beatmap["id"])
                    return
        self.channel.change_beatmap(self.channel.get_beatmap()["id"])

    def update_beatmap(self, message):
        if not self.beatmap_updated:
            self.beatmap_updated = True
            self.channel.set_beatmap(self.channel.get_beatmap())
            while not self.channel.in_progress():
                time.sleep(1)
            self.beatmap_updated = False

    def allow_convert(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.set_allow_convert(True)
            self.channel.send_message("Beatmap conversion set to allowed")

    def disallow_convert(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.set_allow_convert(False)
            self.channel.send_message("Beatmap conversion set to disallowed")

    def allow_unsubmitted(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.set_allow_unsubmitted(True)
            self.channel.send_message("Allow unsubmitted beatmaps set to True")

    def disallow_unsubmitted(self, message):
        if self.channel.has_referee(message["username"]):
            self.channel.set_allow_unsubmitted(False)
            self.channel.send_message("Allow unsubmitted beatmaps set to False")

    def make_room(self, message):
        if self.bot.get_username() == message["username"]:
            command = message["content"].split(" ", 1)[0]
            title = message["content"].replace(command, "", 1).strip()
            channel = self.bot.make_room(title=title)
            channel.set_command("*implement", self.implement_logic_profile, "Implements a logic profile")
            channel.set_command("*logic_profiles", self.get_logic_profiles, "Shows available logic profiles")

    def join(self, message):
        if self.bot.get_username() == message["username"]:
            command = message["content"].split(" ", 1)[0]
            channel = message["content"].replace(command, "", 1).strip()
            if channel[0] != "#":
                channel = "#" + channel
            chan = self.bot.join(channel)
            chan.set_command("*implement", self.implement_logic_profile, "Implements a logic profile")
            chan.set_command("*logic_profiles", self.get_logic_profiles, "Shows available logic profiles")
            self.bot.send_personal_message(self.bot.get_username(), "Bot joined: " + channel)

    def clone(self, message):
        if self.bot.get_username() == message["username"]:
            command = message["content"].split(" ", 1)[0]
            chan = message["content"].replace(command, "", 1).strip()
            if chan:
                if chan[0] != "#":
                    chan = "#" + chan
                if self.bot.has_channel(chan):
                    self.bot.clone_channel(self.bot.get_channel(chan), self.channel)
                    self.channel.send_message("Successfully cloned logic and attributes from " + chan)
                else:
                    self.channel.send_message("Channel: " + chan + " is not recognised. Maybe you need to join it first.")

    def fight(self, message):
        command = message["content"].split(" ", 1)[0]
        user = message["content"].replace(command, "", 1).strip()
        if user:
            if self.channel.has_user(user) and user.replace(" ", "_") != message["username"]:
                self.channel.send_message(message["username"] + " ⚔ fights ⚔ " + user + "...")
                contenders = [message["username"], user]
                actions = ["clobbered", "battered", "pulverized", "destroyed", "thrashed", "hammered", "annihilated", "served", "beat up", "killed", "murdered", "decapitated"]
                choice = random.randint(0, len(actions) - 1)

                victor = contenders[choice % 2]
                if victor.replace(" ", "_") not in self.fights:
                    self.fights[victor.replace(" ", "_")] = 0
                self.fights[victor.replace(" ", "_")] += 1
                contenders.remove(victor)
                self.channel.send_message("✊" + victor + " " + actions[choice] + " " + contenders[0] + "☠! | " + victor + " has defeated " + str(self.fights[victor.replace(" ", "_")]) + " opponents.")
            else:
                self.channel.send_message("User not recognised")
        else:
            if message["username"] not in self.fights:
                self.fights[message["username"]] = 0
            self.channel.send_message(message["username"] + " has defeated " + str(self.fights[message["username"]]) + " opponents.")

    # todo
    def upload_logic_profile(self, message):
        f = open("logic_profiles" + os.sep + self.channel.get_logic_profile() + ".py", "r")
        text = f.read()
        f.close()
        url = self.bot.paste2_upload(self.channel.get_logic_profile() + " logic profile", text)
        self.channel.send_message("The current logic profile is [" + url + " " + self.channel.get_logic_profile() + "]")