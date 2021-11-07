class AutoHostRotate:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.set_beatmap_checker(True)
        channel.maintain_password(True)
        channel.maintain_size(True)
        self.queue = channel.get_users().copy()
        self.skip_vote = channel.hold_vote(self.carry_skip_vote)
        self.start_vote = channel.hold_vote(self.carry_start_vote)
        self.abort_vote = channel.hold_vote(self.carry_abort_vote)
        channel.set_beatmap_checker(True)
        channel.set_command("!q", self.show_queue, "Shows the current queue of players")
        channel.set_command("!queue", self.show_queue, "Shows the current queue of players")
        channel.set_command("!skip", self.skip, "If you are host, changes the host to the next username in the queue else starts vote to skip current host")
        channel.set_command("!config", channel.common_commands.config_link,"Returns a link to the game room configuration page")
        channel.set_command("!randmap", channel.common_commands.randmap,"When host or referee, searches for a random beatmap matching the room's limits and ranges")
        channel.set_command("!altlink", channel.common_commands.altlink,"Returns an alternate link for the current beatmap from chimu.moe")
        channel.set_command("!topdiff", channel.common_commands.topdiff,"When host, upgrades the beatmap to the highest difficulty within the room limits and ranges")
        channel.set_command("!start", self.start,"When host starts the game with optional countdown timer else starts vote to start match")
        channel.set_command("!aborttimer", channel.common_commands.abort_start_timer,"When host or referee, aborts start timer")
        channel.set_command("!abort", self.abort, "Starts vote to abort match")
        channel.set_command("R̲e̲f̲e̲r̲e̲e̲ C̲o̲m̲m̲a̲n̲d̲s̲", "")
        channel.set_command("*skip", self.skip, "Changes the host to the next username in the queue")
        channel.set_command("*implement", channel.common_commands.implement_logic_profile, "Implements a logic profile")
        channel.set_command("*logic_profiles", channel.common_commands.get_logic_profiles, "Shows available logic profiles")
        channel.set_command("*ar_range", channel.common_commands.ar_range, "Sets the ar range for the room. e.g. *ar_range 5.5 8")
        channel.set_command("*od_range", channel.common_commands.od_range, "Sets the od range for the room. e.g. *od_range 5.5 8")
        channel.set_command("*hp_range", channel.common_commands.hp_range, "Sets the hp range for the room. e.g. *hp_range 5.5 8")
        channel.set_command("*cs_range", channel.common_commands.cs_range, "Sets the cs range for the room. e.g. *cs_range 5.5 8")
        channel.set_command("*bpm_range", channel.common_commands.bpm_range, "Sets the bpm range for the room. e.g. *bpm_range 80 120")
        channel.set_command("*diff_range", channel.common_commands.diff_range, "Sets the difficulty range for the room. e.g. *diff_range 4 5.99")
        channel.set_command("*length_range", channel.common_commands.length_range, "Sets the length range for the room in seconds. e.g. *length_range 0 600")
        channel.set_command("*map_status", channel.common_commands.map_status, "Sets the allowed map statuses for the room. e.g. *map_status ranked loved")
        channel.set_command("*mods", channel.common_commands.mods, "Sets the allowed mods for the room. e.g. *mods freemod")
        channel.set_command("*scoring_type", channel.common_commands.scoring_type, "Sets the allowed scoring mode for the room. e.g. *scoring_type score")
        channel.set_command("*team_type", channel.common_commands.team_type, "Sets the allowed team mode for the room. e.g. *team_type head-to-head")
        channel.set_command("*game_mode", channel.common_commands.game_mode, "Sets the allowed game mode for the room. e.g. *game_mode osu taiko")
        channel.set_command("*start_broadcast", channel.common_commands.add_broadcast, "Starts a broadcast in the channel. e.g. *start_broadcast 5 message sent every 5min")
        channel.set_command("*stop_broadcast", channel.common_commands.del_broadcast, "Stops a broadcast in the channel given it's ID. e.g. *stop_broadcast 0")
        channel.set_command("*welcome", channel.common_commands.welcome_message, "Sets the welcome message for the room. e.g. *welcome welcome to my osu room!")
        channel.set_command("*disable_beatmap_checker", channel.common_commands.disable_beatmap_checker, "Disables beatmap checker")
        channel.set_command("*enable_beatmap_checker", channel.common_commands.disable_beatmap_checker, "Enables beatmap checker")
        channel.set_command("*add_artist_whitelist", channel.common_commands.add_artist_whitelist, "Adds an artist to the whitelist. e.g. *add_artist_whitelist eminem")
        channel.set_command("*add_artist_blacklist", channel.common_commands.add_artist_blacklist, "Adds an artist to the blacklist. e.g. *add_artist_blacklist eminem")
        channel.set_command("*add_creator_whitelist", channel.common_commands.add_beatmap_creator_whitelist, "Adds a beatmap creator to the whitelist. e.g. *add_creator_whitelist sotarks")
        channel.set_command("*add_creator_blacklist", channel.common_commands.add_beatmap_creator_blacklist, "Adds a beatmap creator to the blacklist. e.g. *add_creator_blacklist sotarks")
        channel.set_command("*del_artist_whitelist", channel.common_commands.del_artist_whitelist, "Removes an artist from the whitelist. e.g. *del_artist_whitelist eminem")
        channel.set_command("*del_artist_blacklist", channel.common_commands.del_artist_blacklist, "Removes an artist from the blacklist. e.g. *del_artist_blacklist eminem")
        channel.set_command("*del_creator_whitelist", channel.common_commands.del_beatmap_creator_whitelist, "Removes a beatmap creator from the whitelist. e.g. *del_creator_whitelist sotarks")
        channel.set_command("*del_creator_blacklist", channel.common_commands.del_beatmap_creator_blacklist, "Removes a beatmap creator from the blacklist. e.g. *del_creator_blacklist sotarks")

    def show_queue(self, message):
        if self.queue:
            self.channel.send_message("The current queue is: " + ", ".join(self.queue))

    def skip(self, message):
        if message["username"] == self.channel.get_formatted_host() or (message["content"] == "*skip" and self.channel.has_referee(message["username"])):
            if self.queue:
                self.queue.append(self.queue.pop(0))
                self.channel.change_host(self.queue[0])
                self.skip_vote.stop()
        else:
            if not self.skip_vote.is_in_progress():
                self.skip_vote.start()
            if self.skip_vote.cast_ballot(message["username"]):
                self.channel.send_message(str(len(self.skip_vote.get_results())) + " / " + str(self.skip_vote.get_threshold()) + " votes needed to skip the current host")

    def carry_skip_vote(self, vote_manager):
        if self.queue:
            self.queue.append(self.queue.pop(0))
            self.channel.change_host(self.queue[0])

    def start(self, message):
        if message["username"] == self.channel.get_formatted_host():
            self.channel.common_commands.start_timer(message)
        else:
            if not self.start_vote.is_in_progress():
                self.start_vote.start()
            if self.start_vote.cast_ballot(message["username"]):
                self.channel.send_message(str(len(self.start_vote.get_results())) + " / " + str(self.start_vote.get_threshold()) + " votes needed to start the match")

    def abort(self, message):
        if self.channel.in_progress():
            if not self.abort_vote.is_in_progress():
                self.abort_vote.start()
            if self.abort_vote.cast_ballot(message["username"]):
                self.channel.send_message(str(len(self.abort_vote.get_results())) + " / " + str(self.abort_vote.get_threshold()) + " votes needed to end the match")

    def carry_abort_vote(self, vote_manager):
        self.channel.abort_match()

    def carry_start_vote(self, vote_manager):
        self.channel.start_match(10)

    def on_join(self, username):
        self.queue.append(username)
        if self.channel.get_users() == [username]:
            self.channel.change_host(self.queue[0])

    def on_part(self, username):
        if self.queue[0] == username and len(self.queue) > 1 and not self.channel.in_progress():
            self.queue.remove(username)
            self.channel.change_host(self.queue[0])
        else:
            self.queue.remove(username)
        if self.skip_vote.is_in_progress():
            self.channel.send_message(str(self.skip_vote.get_threshold()) + " votes now needed to skip the current beatmap").replace("1 votes", "1 vote", 1)
        if self.start_vote.is_in_progress():
            self.channel.send_message(str(self.start_vote.get_threshold()) + " votes now needed to start the match").replace("1 votes", "1 vote", 1)

    def on_match_start(self):
        self.start_vote.stop()
        self.skip_vote.stop()

    def on_match_finish(self):
        if self.queue:
            if self.queue[0] == self.channel.get_host():
                self.queue.append(self.queue.pop(0))
            self.channel.change_host(self.queue[0])
        self.abort_vote.stop()

    def on_match_abort(self):
        self.on_match_finish()

    def on_host_change(self, old_host, new_host):
        if not self.channel.has_referee(new_host) and new_host != self.queue[0]:
            self.channel.change_host(self.queue[0])
            self.channel.send_message(old_host + " please type '!skip' if you want to skip your turn")
