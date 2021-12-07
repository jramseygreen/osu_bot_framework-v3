import hashlib
import base64
import socket
import struct
import six
import threading


class ws_server:
    def __init__(self, host='localhost', port=8080, on_message_function=None):
        self.__running = True
        self.__host = host
        self.__port = port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__on_message_function = on_message_function
        self.__clients = []

    def __handshake(self, conn):
        request = conn.recv(1024).strip()

        specificationGUID = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        websocketKey = b''

        lines = request.splitlines()
        for line in lines:
            args = line.partition(b': ')
            if args[0] == b'Sec-WebSocket-Key':
                websocketKey = args[2]
                break

        fullKey = hashlib.sha1((websocketKey + specificationGUID)).digest()
        b64Key = base64.b64encode(fullKey)

        response = b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + b64Key + b'\r\n\r\n'
        conn.send(response)

    def __ws_encode(self, data=""):
        if isinstance(data, six.text_type):
            data = data.encode('utf-8')

        length = len(data)
        fin, rsv1, rsv2, rsv3, opcode = 1, 0, 0, 0, 0x1

        frame_header = chr(fin << 7 | rsv1 << 6 | rsv2 << 5 | rsv3 << 4 | opcode)

        if length < 0x7e:
            frame_header += chr(0 << 7 | length)
            frame_header = six.b(frame_header)
        elif length < 1 << 16:
            frame_header += chr(0 << 7 | 0x7e)
            frame_header = six.b(frame_header)
            frame_header += struct.pack("!H", length)
        else:
            frame_header += chr(0 << 7 | 0x7f)
            frame_header = six.b(frame_header)
            frame_header += struct.pack("!Q", length)

        return frame_header + data

    def __ws_decode(self, data):
        frame = bytearray(data)

        length = frame[1] & 127


        indexFirstMask = 2
        if length == 126:
            indexFirstMask = 4
        elif length == 127:
            indexFirstMask = 10

        indexFirstDataByte = indexFirstMask + 4
        mask = frame[indexFirstMask:indexFirstDataByte]

        i = indexFirstDataByte
        j = 0
        decoded = []
        while i < len(frame):
            decoded.append(frame[i] ^ mask[j % 4])
            i += 1
            j += 1

        return "".join(chr(byte) for byte in decoded)

    def __client_thread(self, conn):
        self.__clients.append(conn)
        try:
            while True:
                msg = conn.recv(2046)
                self.__on_message_function(conn, self.__ws_decode(msg))
        except:
            self.__clients.remove(conn)
            conn.close()

    def listen(self, running=False):
        if not running:
            x = threading.Thread(target=self.listen, args=(True,))
            x.setDaemon(True)
            x.start()
        else:
            self.__sock.bind((self.__host, self.__port))
            self.__sock.listen()
            while self.__running:
                conn, addr = self.__sock.accept()
                self.__handshake(conn)
                x = threading.Thread(target=self.__client_thread, args=(conn,))
                x.setDaemon(True)
                x.start()

    def send(self, conn, message):
        conn.send(self.__ws_encode(message))

    def on_message(self, func):
        self.__on_message_function = func

    def get_clients(self):
        return self.__clients

    def set_port(self, port):
        self.__port = port

    def get_port(self):
        return self.__port

    def get_host(self):
        return self.__host
