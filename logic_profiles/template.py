class Template:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.set_command("!command", self.on_command, "!command description")

    def on_command(self, message):
        pass


    def on_personal_message(self, message):
        pass

    def on_message(self, message):
        pass

    def on_join(self, username):
        pass

    def on_part(self, username):
        pass

    def on_match_start(self):
        pass

    def on_match_finish(self):
        pass

    def on_match_abort(self):
        pass

    def on_host_change(self, old_host, new_host):
        pass

    def on_team_change(self, username, team):
        pass

    def on_team_addition(self, username, team):
        pass

    def on_slot_change(self, username, slot):
        pass

    def on_all_players_ready(self):
        pass

    def on_beatmap_change(self, old_beatmap, new_beatmap):
        pass

    def on_changing_beatmap(self):
        pass

    def on_room_close(self):
        pass

    def on_clear_host(self, old_host):
        pass