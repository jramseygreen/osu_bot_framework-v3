# any code here will run on starting the framework
def startup(bot):
    bot.start()
    # Add below line
    # ---------------------------------------------
    channel = bot.make_room(title="4 - 5.99* | AutoSong lobby | Ranked & Loved", password="abc", size=8, beatmapID=bot.chimu.fetch_random_beatmap()["BeatmapId"], mods=["freemod"], game_mode="osu", team_type="head-to-head", scoring_type="score")
    #channel = bot.join("#mp_93542641")
    channel.implement_logic_profile("AutoSong")
    channel.set_diff_range((4, 5.99))
    channel.set_length_range((0, 360))
    channel.set_map_status(["ranked", "loved"])
    channel.set_ar_range((8.9, 9.5))
    channel.set_cs_range((3, 5))
    #print(bot.get_logic_profiles())

    print(channel.get_config_link())
    print(channel.get_users())