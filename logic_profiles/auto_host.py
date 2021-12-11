class Template:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.set_command("!add", self.on_add, "!command description")
        channel.start_on_players_ready(True)

        self.queue = []
        self.requested = []

    def on_add(self, message):
        beatmap = {}
        if len(message["content"].replace("!add").strip()) == 1:
            beatmap = self.channel.fetch_beatmap()
        if self.channel.beatmap_checker_on():
            error = self.channel.check_beatmap(beatmap)


    def on_personal_message(self, message):
        pass

    def on_message(self, message):
        pass

    def on_join(self, username, slot):
        if self.channel.get_users() == [username]:
            self.channel.clear_host()

    def on_part(self, username, slot):
        pass

    def on_match_start(self):
        pass

    def on_match_finish(self):
        pass

    def on_match_abort(self):
        self.on_match_finish()

    def on_host_change(self, old_host, new_host):
        pass

    def on_team_change(self, username, team):
        pass

    def on_team_addition(self, username, team):
        pass

    def on_slot_change(self, username, slot):
        pass

    def on_beatmap_change(self, old_beatmap, new_beatmap):
        pass

    def on_changing_beatmap(self):
        pass

    def on_room_close(self):
        pass

    def on_clear_host(self, old_host):
        pass

    def on_rule_violation(self, error):
        pass
