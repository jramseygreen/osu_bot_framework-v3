class LinearHostRotate:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self.slots = ["" for i in range(16)]
        self.current_host = 0

    def on_join(self, username, slot):
        if self.channel.get_users() == [username]:
            self.channel.set_host(username)
        self.slots[slot] = username

    def on_part(self, username, slot):
        if self.channel.get_host() == username and self.channel.has_users():
            slotnum = self.channel.get_next_full_slot_num(slot + 1)
            self.current_host = slotnum
            self.channel.set_host(self.slots[slotnum])

    def on_match_finish(self):
        if self.channel.has_users():
            slotnum = self.channel.get_next_full_slot_num(self.channel.get_slot_num(self.channel.get_host()) + 1)
            self.current_host = slotnum
            self.channel.set_host(self.slots[slotnum])

    def on_match_abort(self):
        self.on_match_finish()

    def on_host_change(self, old_host, new_host):
        if self.channel.get_slot_num(new_host) != self.current_host:
            self.channel.set_host(old_host)
            self.channel.send_message(old_host + " please pass host directly down!")