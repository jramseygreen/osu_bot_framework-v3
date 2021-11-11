import socket
import threading
import time


# This class prevents rate limit problems / spam silences.
# It is thread safe and guarentees to send messages in the correct order.
class Sock:
    def __init__(self, a=socket.AF_INET, b=socket.SOCK_STREAM):
        self.MSG_NUM = 9  # number of messages to send within the period
        self.PERIOD = 5  # the period of time in seconds to send messages in

        self.__socket = socket.socket(a, b)
        self.__then = 0.0
        self.__semaphore = threading.Semaphore(self.MSG_NUM)
        self.__lock = threading.Lock()
        self.__outbound_queue = []

    def get_socket(self):
        return self.__socket

    # adds the message to the queue and then waits to gain a
    # semaphore + subsequent lock to send the first item in the queue.
    # waits to release semaphore based on rate limit period.
    # lock used to guarantee message order.
    def sendall(self, message, running=False):
        if not running:
            self.__outbound_queue.append(message)
            threading.Thread(target=self.sendall, args=(message, True,)).start()
        else:
            self.__semaphore.acquire()
            self.__lock.acquire()
            time.sleep(0.1)
            self.__socket.sendall(self.__outbound_queue.pop(0))
            self.__lock.release()
            if time.time() - self.__then >= self.PERIOD:
                self.__then = time.time()
            time.sleep(self.PERIOD - (time.time() - self.__then))
            self.__semaphore.release()

    def set_msg_num(self, num):
        self.MSG_NUM = num

    def set_period(self, secs):
        self.PERIOD = secs