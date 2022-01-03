import collections
import bson
from bson.codec_options import CodecOptions
import os,socket,threading, struct
from threading import Thread

#	         			data2 = bson.encode({'ID': 'BGM', 'CmB': {'nick': '[SERVER]', 'userID': 'SN7O6FBR', 'channel': 'UMG', 'channelIndex': 1, 'message': 'TESTING 12333333', 'time': 'datetime.datetime(2022, 1, 2, 1, 7, 55, 902000)'}})
#	         			buf = bytearray(4 + len(data2))
#	         			buf[0:4] = struct.pack('<I', 4 + len(data2))
#	         			buf[4:] = data2
#	         			sok.sendall(buf)

#example data
def write_log(text):
	a = open('logs.txt', 'a+')
	a.write(text)
	a.close()
def ServerBsonHandler(data):
	try:
	         msgCount = int(data["mc"])
	         for i in range(msgCount):
	         	current = data['m' + str(i)]
	         	messageId = current["ID"];
	         	z = '[SERVER] MESSAGE ID: ' + messageId + ' Data: ' + str(current)
	         	print(z)
	         	write_log(z + '\n')
	except Exception as e:
		print('[SERVER HANDLER] ', e)
		
def ClientBsonHandler(data, sok):
	try:
	         msgCount = int(data["mc"]);
	         for i in range(msgCount):
	         	current = data['m' + str(i)]
	         	messageId = current["ID"];
	         	ot = '[CLIENT] MESSAGE ID: ' + messageId + ' Data: ' + str(data)
	         	print(ot)
	         	write_log(ot + '\n')
	except Exception as e:
		print(e)
class Proxy2Server(Thread):

    def __init__(self, host, port):
        super(Proxy2Server, self).__init__()
        self.game = None
        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    def run(self):
        while True:
            data = self.server.recv(9999999)
            if data:
                try:
                	dec = bson.decode(data[4:])
                	print('Server: ' + str(dec))
                	ServerBsonHandler(dec)
                except Exception as e:
                    print 
                    ('server[{}]'.format(self.port), e)
                self.game.sendall(data)

class Game2Proxy(Thread):

    def __init__(self, host, port):
        super(Game2Proxy, self).__init__()
        self.server = None
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        # waiting for a connection
        self.game, addr = sock.accept()

    def run(self):
        while True:
            data = self.game.recv(9999999)
            if data:
                try:
                    dec = bson.decode(data[4:])
                    ClientBsonHandler(dec, self.game)
                except Exception as e:
                    print('client[{}]'.format(self.port), e)
                self.server.sendall(data)

class Proxy(Thread):

    def __init__(self, from_host, to_host, port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port

    def run(self):
        while True:
            print("[proxy({})] setting up".format(self.port))
            self.g2p = Game2Proxy(self.from_host, self.port) # waiting for a client
            self.p2s = Proxy2Server(self.to_host, self.port)
            print("[proxy({})] connection established".format(self.port))
            self.g2p.server = self.p2s.server
            self.p2s.game = self.g2p.game

            self.g2p.start()
            self.p2s.start()
            
master_server = Proxy('127.0.0.1', '44.194.163.69', 10001)
master_server.start()
while True:
    try:
        cmd = input('$ ')
        if cmd[:4] == 'quit':
            os._exit(0)
    except Exception as e:
        print(e)
