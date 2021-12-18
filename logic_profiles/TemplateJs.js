Template = {
    constructor: function (bot, channel) {
        this.bot = bot;
        this.channel = channel;

        channel.set_command("!command", this.on_command, "!command description");
    },
    
    on_command: function (message) {
        return;
    },

    // runs when a personal message is received
    // message is a dictionary containing the username, channel and message
    // channel parameter in message dictionary is the bot username
    on_personal_message: function (message) {
        return;
    },

    // runs when a message is received in the channel
    // message is a dictionary containing the username, channel and message
    on_message: function (message) {
        return;
    },
    // runs when a user joins the channel
    // slot is an integer of the slot number joined
    // username is a string of the user's username who joined
    on_join: function (username, slot) {
        return;
    },

    // runs when a user leaves the channel
    // slot is an integer of the slot number joined
    // username is a string of the user's username who joined
    on_part: function (username, slot) {
        return;
    },

    // runs when the match is started
    on_match_start: function () {
        return;
    },

    // runs when the match finishes normally
    on_match_finish: function () {
        return;
    },

    // runs when a match is aborted with either a command or the method channel.abort_match()
    on_match_abort: function () {
        return;
    },

    // runs when the host is changed
    // old_host is the username of the user who had host before the change
    // new_host is the username of the user who has just received host
    on_host_change: function (old_host, new_host) {
        return;
    },

    // runs when a user changes team
    // username is the username of the user who changed team
    // team is the colour of the team joined
    on_team_change: function (username, team) {
        return;
    },

    // runs when a user is added to a team
    // username is the username of the user who changed team
    // team is the colour of the team joined
    on_team_addition: function (username, team) {
        return;
    },

    // runs when a user changes slot
    // slot is an integer of the slot number joined
    // username is a string of the user's username who joined
    on_slot_change: function (username, slot) {
        return;
    },

    // runs when all players in the room have readied up
    on_all_players_ready: function () {
        return;
    },

    // runs when the beatmap is changed
    // old beatmap is the previous beatmap before the change
    // new_beatmap is the beatmap which hasw just been changed to
    on_beatmap_change: function (old_beatmap, new_beatmap) {
        return;
    },

    // runs when host enters map select
    on_changing_beatmap: function () {
        return;
    },

    // runs when a game room is closed
    on_room_close: function () {
        return;
    },

    // runs when the host is cleared
    // old_host is the host prior to clearing the room
    on_clear_host: function (old_host) {
        return;
    },

    // runs when an enforced attribute is violated
    // error contains:
    // type - the type of on_rule_violation
    // message - a message to explain what is going on
    on_rule_violation: function (error) {
        return;
    }
}