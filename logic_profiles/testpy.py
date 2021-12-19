def __init__(self, bot, channel):
    self.bot = bot
    self.channel = channel

    self.queue = []

    # add a command with a method
    channel.set_command("!queue", self.show_queue, "Shows the queue of players")


# method to execute when !queue command is received
def show_queue(self):
    # send the queue of players to the channel
    self.channel.send_message("The current queue is: " + ", ".join(self.queue))


def on_join(username):
    self.queue.append(username)

    # check if the game room only has the new user in it
    if self.channel.get_users() == [username]:
        # give them the host
        self.channel.set_host(username)


def on_part(username):
    self.queue.remove(username)

    # check if the leaving user is host and there are still users in the game room and game is not in progress
    if self.channel.is_host(username) and self.channel.has_users() and not self.channel.in_progress():
        # change the host to the top of the queue
        self.set_host(queue[0])


def on_match_finish():
    # rotate the queue
    self.queue.append(self.queue.pop(0))

    # set the new host
    self.channel.set_host(queue[0])