import json
import random
import time

import requests

class AutoSong:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel

        channel.set_custom_config("In this lobby beatmaps are selected for you at random by the bot.\nYou can vote to skip a beatmap with the !skip command.\n\n\n")
        channel.set_command("!info", "Built with [https://github.com/jramseygreen/osu_bot_framework-v3 osu_bot_framework v3] | Type '!config' to view room configuration and commands", "Built with osu bot framework v3")
        channel.set_command("!skip", self.skip, "Vote to skip the current beatmap.")
        channel.set_command("!altlink", channel.common_commands.altlink, "returns an alternate link for the current beatmap from chimu.moe")
        channel.set_command("!config", channel.common_commands.config_link, "returns a link to the game room configuration page")
        channel.set_command("R̲e̲f̲e̲r̲e̲e̲ C̲o̲m̲m̲a̲n̲d̲s̲", "")
        channel.set_command("*implement", channel.common_commands.implement_logic_profile, "Implements a logic profile")
        channel.set_command("*logic_profiles", channel.common_commands.get_logic_profiles, "Shows available logic profiles")
        channel.set_command("*aborttimer", channel.common_commands.abort_start_timer, "Aborts start timer")
        channel.set_command("*skip", self.skip, "Skips the current beatmap")
        channel.set_command("*game_mode", channel.common_commands.game_mode, "Sets the game mode of the lobby")
        channel.set_command("*diff_range", channel.common_commands.diff_range,"Sets the difficulty range for the room. e.g. *diff_range 4 5.99")
        channel.set_command("*map_status", channel.common_commands.map_status, "Sets the allowed map statuses for the room. e.g. *map_status ranked loved")
        channel.set_command("*add_artist_whitelist", channel.common_commands.add_artist_whitelist,"Adds an artist to the whitelist. e.g. *add_artist_whitelist eminem")
        channel.set_command("*add_artist_blacklist", channel.common_commands.add_artist_blacklist, "Adds an artist to the blacklist. e.g. *add_artist_blacklist eminem")
        channel.set_command("*add_creator_whitelist", channel.common_commands.add_beatmap_creator_whitelist, "Adds a beatmap creator to the whitelist. e.g. *add_creator_whitelist sotarks")
        channel.set_command("*add_creator_blacklist", channel.common_commands.add_beatmap_creator_blacklist, "Adds a beatmap creator to the blacklist. e.g. *add_creator_blacklist sotarks")
        channel.set_command("*del_artist_whitelist", channel.common_commands.del_artist_whitelist,"Removes an artist from the whitelist. e.g. *del_artist_whitelist eminem")
        channel.set_command("*del_artist_blacklist", channel.common_commands.del_artist_blacklist, "Removes an artist from the blacklist. e.g. *del_artist_blacklist eminem")
        channel.set_command("*del_creator_whitelist", channel.common_commands.del_beatmap_creator_whitelist, "Removes a beatmap creator from the whitelist. e.g. *del_creator_whitelist sotarks")
        channel.set_command("*del_creator_blacklist", channel.common_commands.del_beatmap_creator_blacklist,"Removes a beatmap creator from the blacklist. e.g. *del_creator_blacklist sotarks")
        channel.set_command("*welcome", channel.common_commands.welcome_message, "Sets the welcome message for the room. e.g. *welcome welcome to my osu room!")

        self.vote = channel.new_vote_manager(self.carry_vote)
        self.played = []

        channel.set_beatmap_checker(False)
        channel.start_on_players_ready(True)
        channel.clear_host()
        channel.set_allow_unsubmitted(False)
        channel.set_allow_convert(False)
        channel.set_autostart_timer(True, 120)
        self.next_round()

    def skip(self, message):
        if self.channel.has_referee(message["username"]) and message["content"] == "*skip":
            self.carry_vote(None)
        elif not self.channel.in_progress():
            self.vote.cast_ballot(message["username"], "Skip beatmap")

    def on_join(self, username):
        if self.channel.get_users() == [username]:
            self.next_round()

    def on_match_finish(self):
        self.next_round()

    def on_match_start(self):
        self.vote.stop()

    def next_round(self):
        beatmap = self.bot.chimu.fetch_random_beatmap(self.channel)
        if beatmap:
            if beatmap in self.played:
                beatmap = self.bot.chimu.fetch_random_beatmap(self.channel)
            self.played.append(beatmap)
            self.channel.send_message("!mp map " + str(beatmap["BeatmapId"]) + " | The next beatmap is [https://osu.ppy.sh" + beatmap["DownloadPath"] + " " + beatmap["OsuFile"][:-4] + "] | Type '!skip' to vote to skip this beatmap.")
        else:
            self.channel.send_message("Could not find any beatmaps matching your criteria!")

    def carry_vote(self, vote_manager):
        self.channel.send_message("Beatmap skipped!")
        self.channel.abort_start_timer()
        self.next_round()