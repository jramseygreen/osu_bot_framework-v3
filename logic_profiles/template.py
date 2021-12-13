class Template:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.set_command("!command", self.on_command, "!command description")

    def on_command(self, message):
        pass


    # runs when a personal message is received
    # message is a dictionary containing the username, channel and message
    # channel parameter in message dictionary is the bot username
    def on_personal_message(self, message):
        pass

    # runs when a message is received in the channel
    # message is a dictionary containing the username, channel and message
    def on_message(self, message):
        pass

    # runs when a user joins the channel
    # slot is an integer of the slot number joined
    # username is a string of the user's username who joined
    def on_join(self, username, slot):
        pass

    # runs when a user leaves the channel
    # slot is an integer of the slot number joined
    # username is a string of the user's username who joined
    def on_part(self, username, slot):
        pass

    # runs when the match is started
    def on_match_start(self):
        pass

    # runs when the match finishes normally
    def on_match_finish(self):
        pass

    # runs when a match is aborted with either a command or the method channel.abort_match()
    def on_match_abort(self):
        pass

    # runs when the host is changed
    # old_host is the username of the user who had host before the change
    # new_host is the username of the user who has just received host
    def on_host_change(self, old_host, new_host):
        pass

    # runs when a user changes team
    # username is the username of the user who changed team
    # team is the colour of the team joined
    def on_team_change(self, username, team):
        pass

    # runs when a user is added to a team
    # username is the username of the user who changed team
    # team is the colour of the team joined
    def on_team_addition(self, username, team):
        pass

    # runs when a user changes slot
    # slot is an integer of the slot number joined
    # username is a string of the user's username who joined
    def on_slot_change(self, username, slot):
        pass

    # runs when all players in the room have readied up
    def on_all_players_ready(self):
        pass

    # runs when the beatmap is changed
    # old beatmap is the previous beatmap before the change
    # new_beatmap is the beatmap which hasw just been changed to
    def on_beatmap_change(self, old_beatmap, new_beatmap):
        pass

    # runs when host enters map select
    def on_changing_beatmap(self):
        pass

    # runs when a game room is closed
    def on_room_close(self):
        pass

    # runs when the host is cleared
    # old_host is the host prior to clearing the room
    def on_clear_host(self, old_host):
        pass

    # runs when an enforced attribute is violated
    # error contains:
    # type - the type of on_rule_violation
    # message - a message to explain what is going on
    def on_rule_violation(self, error):
        pass
