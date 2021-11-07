# any code here will run on starting the framework
def startup(bot):
    bot.start()
    # Add below line
    # ---------------------------------------------
    channel = bot.make_room(title="Chill & Practice | 4* - 4.99* | Auto Host Rotate", password="abc", size=16, beatmapID=bot.chimu.fetch_random_beatmap()["BeatmapId"], mods=["freemod"], game_mode="osu", team_type="head-to-head", scoring_type="score")
    #channel = bot.join("#mp_93542641")
    channel.implement_logic_profile("AutoHostRotate")
    channel.set_diff_range((4, 4.99))
    #channel.add_beatmap_creator_blacklist("sotarks")
    #channel.set_length_range((0, 360))
    #channel.set_map_status(["ranked", "loved"])
    #channel.set_ar_range((8.9, 9.5))
    #channel.set_cs_range((3, 5))
    #print(bot.get_logic_profiles())

    print(channel.get_config_link())
    print(channel.get_users())