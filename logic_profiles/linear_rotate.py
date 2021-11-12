class LinearHostRotate:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel

    def on_part(self, username, slot):
        if self.channel.get_host() == username and self.channel.has_users():
            self.channel.set_host(self.channel.get_slots()[self.channel.get_next_full_slot(offset=slot + 1)]["username"])

    def on_match_finish(self):
        if self.channel.has_users():
            self.channel.set_host(self.channel.get_slots()[self.channel.get_next_full_slot(offset=self.channel.get_slot_num(self.channel.get_host()) + 1)]["username"])

    def on_match_abort(self):
        self.on_match_finish()