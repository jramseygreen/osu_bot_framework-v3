# any code here will run on starting the framework
def startup(bot):
    bot.start()
    # Add below line
    # ---------------------------------------------
    #channel = bot.make_room("test3")
    channel = bot.join("#mp_93426772")
    channel.implement_logic_profile("Manager")
    channel.set_diff_range((4, 5.5))
    channel.set_mods("freemod")
    channel.set_game_mode("osu")
    #channel.set_map_status(["pending"])
    #print(bot.get_logic_profiles())

    print(channel.get_config_link())