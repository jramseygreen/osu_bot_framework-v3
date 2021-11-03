import json

from framework import Bot
from config.startup import startup

# inititalisation + grab credentials
f = open("config/bot_config.conf", "r")
config = json.loads(f.read())
f.close()
if not config["password"] or config["password"] == "password":
    print("Please go to http://osu.ppy.sh/p/irc/ and generate your username and password!")
    config["username"] = input("username: ")
    config["password"] = input("password: ")
    if input("Would you like to save these credentials for next time? [y/n]: ") == "y":
        print("You can change your credentials in the future by modifying bot_config.conf")
        f = open("config/bot_config.conf", "w")
        f.write(json.dumps(config).replace(", ", "\n").replace("{", "{\n", 1).replace("}", "\n}"))
        f.close()
# set up bot
bot = Bot(username=config["username"], password=config["password"], host=config["irc_host"], port=config["irc_port"], server_ip=config["server_ip"], message_log_length=config["message_log_length"], verbose=config["verbose"])
bot.set_webapp_port(config["server_port"])
bot.set_websocket_port(config["websocket_port"])
startup(bot)
