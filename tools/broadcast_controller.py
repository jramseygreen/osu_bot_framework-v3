import threading
import time


# controls message broadcasts in channels and PMs
class BroadcastController:
    def __init__(self, bot):
        self.__bot = bot
        self.__channels = {}
        self.__id_lock = threading.Lock()
        self.__id = 0

    # returns the broadcasts associated with a channel or all channels with broadcasts if left blank
    def get_broadcasts(self, channel=""):
        if channel in self.__channels:
            return self.__channels[channel]
        elif not channel:
            return self.__channels
        return []

    # adds a new active broadcast and returns its id
    def add_broadcast(self, channel, message, secs):
        id = self.__gen_id()
        broadcast = {"id": id, "channel": channel, "message": message, "secs": int(secs)}
        if channel not in self.__channels:
            self.__channels[channel] = []
        self.__channels[channel].append(broadcast)
        self.__start_broadcast(broadcast)
        return id

    # deletes a broadcast given its id
    def del_broadcast(self, id):
        channels = self.__channels.copy()
        for channel in channels:
            for broadcast in channels[channel]:
                if broadcast["id"] == int(id):
                    channels[channel].remove(broadcast)
                    if channels[channel] == []:
                        del channels[channel]
                    return

    # returns true if id is currently broadcasting
    def has_id(self, id):
        return self.get_broadcast(id) is not None

    # gets a broadcast based on its id
    def get_broadcast(self, id):
        channels = self.__channels.copy()
        for channel in channels:
            for broadcast in channels[channel]:
                if broadcast["id"] == int(id):
                    return broadcast

    # generates a new unique id. THREAD SAFE
    def __gen_id(self):
        self.__id_lock.acquire()
        id = self.__id
        self.__id += 1
        self.__id_lock.release()
        return id

    # send broadcast messages on threads
    def __start_broadcast(self, broadcast, running=False):
        if not running:
            threading.Thread(target=self.__start_broadcast, args=(broadcast, True,)).start()
        else:
            # end condition
            while self.get_broadcast(broadcast["id"]):
                # if channel broadcast
                if self.__bot.has_channel(broadcast["channel"]):
                    self.__bot.get_channel(broadcast["channel"]).send_message(broadcast["message"])
                # pm broadcast
                elif broadcast["channel"][0] != "#":
                    self.__bot.send_personal_message(broadcast["channel"], broadcast["message"])
                time.sleep(broadcast["secs"])
