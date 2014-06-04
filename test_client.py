import socket
from time import sleep
import random
import string
import json
import threading


def send(ip, port):
    print 'sending'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        BPos = [random.choice(range(400)), random.choice(range(200))]
        PPos = random.choice(range(100))
        msg = "{\"BPos\":[%s,%s], \"PPos\":%s}" % (BPos[0], BPos[1], str(PPos))
        print json.loads(msg)
        sleep(10)
        print msg
        sock.sendto(msg, (ip, port))


def main():
    #send('54.86.251.5', 56565)
    threading.Thread(target=send, args=('54.86.251.5', 56565)).start()
    threading.Thread(target=send, args=('54.86.251.5', 56565)).start()
main()