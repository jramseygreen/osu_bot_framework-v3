import json
import os
from getpass import getpass

from framework import Bot
from config.startup import startup

# initialisation + grab credentials
os.system("title osu bot framework v3")
f = open("config" + os.sep + "bot_config.conf", "r")
config = json.loads(f.read())
f.close()
if not config["password"] or config["password"] == "password":
    print("Please go to http://osu.ppy.sh/p/irc/ and generate your username and password!")
    while not config["password"] or config["password"] == "password":
        config["username"] = input("Enter your irc username: ")
        password = getpass(prompt="Enter your irc password (hidden): ")
        confirm = getpass(prompt="Enter your irc password again to confirm (hidden): ")
        if confirm == password:
            config["password"] = password
        else:
            print("Passwords do not match!")

    if input("Would you like to save these credentials for next time? [y/n]: ").lower() in ["y", "yes"]:
        print("You can change your credentials in the future by modifying ./config/bot_config.conf")
        f = open("config" + os.sep + "bot_config.conf", "w")
        f.write(json.dumps(config).replace(", ", ",\n").replace("{", "{\n", 1).replace("}", "\n}"))
        f.close()
# set up bot
try:
    os.mkdir("config" + os.sep + "logs")
except:
    pass
bot = Bot(username=config["username"], password=config["password"], host=config["irc_host"], port=config["irc_port"], server_ip=config["server_ip"], message_log_length=config["message_log_length"], logging=config["logging"], verbose=config["verbose"])
bot.set_webapp_port(config["server_port"])
bot.set_websocket_port(config["websocket_port"])
bot.get_sock().set_period(config["send_period"])
bot.get_sock().set_msg_num(config["send_cap"])
startup(bot)
