# any code here will run on starting the framework
def startup(bot):
    channel = bot.make_room("test3")
    channel.implement_logic_profile("Template")
    channel.set_diff_range((4, 5))
    channel.add_command("!test", "test command")
    channel.set_map_status(["pending"])
    print(bot.get_logic_profiles())

    print(channel.get_config_link())