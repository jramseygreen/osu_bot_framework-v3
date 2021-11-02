import json

from framework import Bot

# inititalisation + grab credentials
f = open("bot_config.conf", "r")
config = json.loads(f.read())
f.close()
if config["password"] == "password":
    print("Please go to http://osu.ppy.sh/p/irc/ and generate your username and password!")
    config["username"] = input("username: ")
    config["password"] = input("password: ")
    if input("Would you like to save these credentials for next time? [y/n]: ") == "y":
        print("You can change your credentials in the future by modifying bot_config.conf")
        f = open("bot_config.conf", "w")
        f.write(json.dumps(config).replace(", ", "\n").replace("{", "{\n", 1).replace("}", "\n}"))
        f.close()
bot = Bot(username=config["username"], password=config["password"], host=config["irc_host"], port=config["irc_port"], server_ip=config["server_ip"], verbose=config["verbose"])
bot.set_webapp_port(config["server_port"])
bot.set_websocket_port(config["websocket_port"])
bot.start()
channel = bot.make_room("test3")
channel.implement_logic_profile("Template")
channel.set_diff_range((4, 5))
channel.add_command("!test", "test command")
print(bot.get_logic_profiles())

print(channel.get_config_link())