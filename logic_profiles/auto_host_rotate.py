class AutoHostRotate:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self.queue = channel.get_users().copy()
        channel.implement_logic_profile("Manager")
        channel.set_beatmap_checker(True)
        channel.set_command("!q", self.show_queue, "Shows the current queue of players")
        channel.set_command("!queue", self.show_queue,"Shows the current queue of players")
        channel.set_command("!skip", self.skip, "If you are a referee or host, changes the host to the next username in the queue")

    def show_queue(self, message):
        if self.queue:
            self.channel.send_message("The current queue is: " + ", ".join(self.queue))

    def skip(self, message):
        if message["username"] == self.channel.get_formatted_host() or self.channel.is_referee(message["username"]):
            if self.queue:
                self.queue.append(self.queue.pop(0))
                self.channel.change_host(self.queue[0])

    def on_join(self, username):
        self.queue.append(username)
        if self.channel.get_users() == [username]:
            self.channel.change_host(self.queue[0])

    def on_part(self, username):
        if self.queue[0] == username and len(self.queue) > 1 and not self.channel.in_progress():
            self.queue.remove(username)
            self.channel.change_host(self.queue[0])

    def on_match_start(self):
        self.queue.append(self.queue.pop(0))

    def on_match_finish(self):
        if self.queue:
            self.channel.change_host(self.queue[0])

    def on_host_change(self, old_host, new_host):
        if not self.channel.is_referee(new_host) and new_host != self.queue[0]:
            self.channel.change_host(self.queue[0])
            self.channel.send_message(old_host + " please type '!skip' if you want to skip your turn")
