# implements all common commands
class Manager:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        channel.set_beatmap_checker(True)
        channel.set_command("!config", channel.common_commands.config_link, "returns a link to the game room configuration page")
        channel.set_command("!randmap", channel.common_commands.randmap, "searches for a random beatmap matching the room's limits and ranges")
        channel.set_command("!altlink", channel.common_commands.altlink, "returns an alternate link for the current beatmap from chimu.moe")
        channel.set_command("*implement", channel.common_commands.implement_logic_profile, "Implements a logic profile")
        channel.set_command("*logic_profiles", channel.common_commands.get_logic_profiles, "Shows available logic profiles")
        channel.set_command("*ar_range", channel.common_commands.ar_range, "Sets the ar range for the room. e.g. *ar_range 5.5 8")
        channel.set_command("*od_range", channel.common_commands.od_range, "Sets the od range for the room. e.g. *od_range 5.5 8")
        channel.set_command("*hp_range", channel.common_commands.hp_range, "Sets the hp range for the room. e.g. *hp_range 5.5 8")
        channel.set_command("*cs_range", channel.common_commands.cs_range, "Sets the cs range for the room. e.g. *cs_range 5.5 8")
        channel.set_command("*bpm_range", channel.common_commands.bpm_range, "Sets the bpm range for the room. e.g. *bpm_range 80 120")
        channel.set_command("*diff_range", channel.common_commands.diff_range, "Sets the difficulty range for the room. e.g. *diff_range 4 5.99")
        channel.set_command("*length_range", channel.common_commands.length_range, "Sets the length range for the room in seconds. e.g. *length_range 0 600")
        channel.set_command("*map_status", channel.common_commands.map_status, "Sets the allowed map statuses for the room. e.g. *map_status ranked loved")
        channel.set_command("*mods", channel.common_commands.mods, "Sets the allowed mods for the room. e.g. *mods freemod")
        channel.set_command("*scoring_type", channel.common_commands.scoring_type, "Sets the allowed scoring mode for the room. e.g. *scoring_type score")
        channel.set_command("*team_type", channel.common_commands.team_type, "Sets the allowed team mode for the room. e.g. *team_type head-to-head")
        channel.set_command("*game_mode", channel.common_commands.game_mode, "Sets the allowed game mode for the room. e.g. *game_mode osu taiko")
        channel.set_command("*start_broadcast", channel.common_commands.add_broadcast, "Starts a broadcast in the channel. e.g. *start_broadcast 5 message sent every 5min")
        channel.set_command("*stop_broadcast", channel.common_commands.del_broadcast, "Stops a broadcast in the channel given it's ID. e.g. *stop_broadcast 0")
        channel.set_command("*welcome", channel.common_commands.welcome_message, "Sets the welcome message for the room. e.g. *welcome welcome to my osu room!")
