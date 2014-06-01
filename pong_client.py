from pong import Pong
import socket
import threading
from time import sleep
import random

#create a recieve queue and a send queue

def listen(pong, ip, port):
    print 'listening'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    while True:
        data, addr = sock.recvfrom(1024)
        print addr
        print data


def send(ip, port, msg):
    print 'sending'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        print 'send test: ' + msg
        sleep(2)
        sock.sendto(msg, (ip, port))


def main():
    pong = Pong('left')
    while True:
        sleep(3)
        a = random.choice([x for x in range(0, 85)])
        pong.angle = a
        print a

    #s = threading.Thread(target=send, args = (pong, '127.0.0.1', 5005, 'just checking')).start()
    #use the daemon to run this in the background?
    #s.daemon = True
    #s.start()
    #l = threading.Thread(target=listen, args = ('127.0.0.1', 5005)).start()
    #l.daemon = True
    #l.start()
    #spinn off thread for listener
    #app = Pong('left')


main()