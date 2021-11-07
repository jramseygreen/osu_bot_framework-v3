import json

import requests

class AutoSong:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self.vote = channel.hold_vote(self.carry_vote)
        self.played = []
        channel.set_command("!info", "Built with [https://github.com/jramseygreen/osu_bot_framework-v3 osu_bot_framework v3] | Type '!config' to view room configuration and commands", "Built with osu bot framework v3")
        channel.set_command("!skip", self.skip, "Vote to skip the current beatmap.")
        channel.set_command("!altlink", channel.common_commands.altlink, "returns an alternate link for the current beatmap from chimu.moe")
        channel.set_command("!config", channel.common_commands.config_link, "returns a link to the game room configuration page")
        channel.set_command("!update", self.update_beatmap, "Updates the current beatmap to the latest version")
        channel.set_command("R̲e̲f̲e̲r̲e̲e̲ C̲o̲m̲m̲a̲n̲d̲s̲", "")
        channel.set_command("*implement", channel.common_commands.implement_logic_profile, "Implements a logic profile")
        channel.set_command("*logic_profiles", channel.common_commands.get_logic_profiles, "Shows available logic profiles")
        channel.set_command("*aborttimer", channel.common_commands.abort_start_timer, "Aborts start timer")
        channel.set_beatmap_checker(False)

    def update_beatmap(self, message):
        beatmap = self.bot.chimu.fetch_beatmap(self.channel.get_beatmap()["id"])
        if beatmap:
            r = requests.get("https://osu.ppy.sh/s/" + str(beatmap["ParentSetId"]))
            try:
                beatmapset = json.loads(
                    r.text.split('<script id="json-beatmapset" type="application/json">\n        ', 1)[1].split(
                        "\n", 1)[0])
                print(beatmapset)
                for map in beatmapset["maps"]:
                    if map["version"] == beatmap["DiffName"]:
                        self.channel.change_beatmap(map["id"])
                        return
            except:
                pass

            self.channel.change_beatmap(self.channel.get_beatmap()["id"])

    def skip(self, message):
        if not self.channel.in_progress():
            if not self.vote.is_in_progress():
                self.vote.start()

            if self.vote.cast_ballot(message["username"]):
                self.channel.send_message(str(len(self.vote.get_results())) + " / " + str(self.vote.get_threshold()) + " votes needed to skip the current beatmap")

    def on_join(self, username):
        if self.channel.get_users() == [username]:
            self.next_round()

    def on_part(self, username):
        if self.vote.is_in_progress():
            self.channel.send_message(str(self.vote.get_threshold()) + " votes now needed to skip the current beatmap").replace("1 votes", "1 vote", 1)

    def on_match_finish(self):
        self.next_round()

    def on_all_players_ready(self):
        self.channel.start_match()

    def next_round(self):
        beatmap = self.bot.chimu.fetch_random_beatmap(self.channel)
        while beatmap["BeatmapId"] in self.played:
            beatmap = self.bot.chimu.fetch_random_beatmap(self.channel)
        if len(self.played) >= 50:
            self.played.pop(0)
        self.played.append(beatmap["BeatmapId"])
        self.channel.send_message("!mp map " + str(beatmap["BeatmapId"]) + " | The next beatmap is [https://osu.ppy.sh" + beatmap["DownloadPath"] + " " + beatmap["OsuFile"][:-4] + "] | Type '!skip' to vote to skip this beatmap.")
        self.channel.start_match(120)

    def carry_vote(self, vote_manager):
        self.channel.send_message("Vote carried with " + str(vote_manager.get_threshold()) + " votes")
        self.channel.abort_start_timer()
        self.next_round()