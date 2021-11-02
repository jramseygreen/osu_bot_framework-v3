from framework import Bot

bot = Bot(username="username", password="password", verbose=True)
bot.start()
channel = bot.make_room("test3")
channel.set_diff_range((4, 5))
channel.add_command("!test", "test command")
channel.implement_logic_profile("Test")
print(bot.get_logic_profiles())

print(channel.get_config_link())