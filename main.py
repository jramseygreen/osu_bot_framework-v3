from framework import Bot

# inititalisation + grab credentials
username = ""
password = ""
f = open("credentials.txt", "r")
credentials = f.read().split(":")
f.close()
if len(credentials) == 2 and credentials != ["username", "password"]:
    username = credentials[0]
    password = credentials[1]
else:
    print("Please go to http://osu.ppy.sh/p/irc/ and generate your username and password!")
    username = input("username: ")
    password = input("password: ")
    if input("Would you like to save these credentials for next time? [y/n]: ") == "y":
        print("You can change your credentials in the future by modifying credentials.txt")
        f = open("credentials.txt", "w")
        f.write(username + ":" + password)
        f.close()

bot = Bot(username=username, password=password, verbose=True)
bot.start()
channel = bot.make_room("test3")
channel.set_diff_range((4, 5))
channel.add_command("!test", "test command")
print(bot.get_logic_profiles())

print(channel.get_config_link())