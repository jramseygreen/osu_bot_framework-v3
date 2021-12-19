LogicProfile = {
    constructor: function (bot, channel) {
        LogicProfile.bot = bot;
        LogicProfile.channel = channel;
        // add a command with a method
        channel.set_command("!queue", LogicProfile.show_queue, "Shows the queue of players")

        LogicProfile.queue = [];
    },
    show_queue: function () {
        LogicProfile.channel.send_message("The current queue is: " + LogicProfile.queue.join(", "));
    },
    on_join: function (username) {
        LogicProfile.queue.push(username);

        // check if the game room only has 1 user in it
        if (LogicProfile.channel.get_users().length === 1) {
            // give them the host
            LogicProfile.channel.set_host(username);
        }
    },

    on_part: function (username) {
        LogicProfile.queue.splice(LogicProfile.queue.indexOf(username), 1);

        // check if the leaving user is host and the game room still has users and the match is not in progress
        if (LogicProfile.channel.is_host(username) && LogicProfile.channel.has_users() && !LogicProfile.channel.in_progress()) {
            // change the host to the top of the queue
            LogicProfile.channel.set_host(queue[0]);
        }
    },

    on_match_finish: function () {
        // rotate the queue
        LogicProfile.queue.push(LogicProfile.queue.shift());

        // set the new host
        LogicProfile.channel.set_host(LogicProfile.queue[0]);
    },
};