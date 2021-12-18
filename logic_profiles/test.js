LogicProfile = {
    constructor: function(bot, channel) {
        LogicProfile.bot = bot;
        LogicProfile.channel = channel;

        channel.set_command("!simple_command", "Text to send as a response", "A description of the command")
        channel.set_command("!advanced_command", LogicProfile.response_method, "A description of the command")
    },
    response_method: function (message) {
        LogicProfile.channel.send_message(message.username + " sent " + message.content + " in " + message.channel)
    }
  };