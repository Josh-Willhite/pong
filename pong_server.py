import socket
import json
import threading
from time import sleep
from Queue import Queue

player_queue = Queue()


def listen(ip, port):
    print 'listening:%s:%s' % (str(ip), str(port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    while True:
        data, addr = sock.recvfrom(1024)
        print addr
        print data

        msg_recv = json.loads(data)

        if msg_recv['ACTION'] == 'ADD':
            print msg_recv
            entry = [msg_recv['PLAYER'], addr]
            player_queue.put(entry)


        if msg_recv['ACTION'] == 'LIST':
            players = []
            while not player_queue.empty():
                players.append(player_queue.get())

            msg = {'SERVER':ip, 'ACTION':'LIST', 'OPPONENTS':players}

            for player in players:
                player_queue.put(player)
                if player[0] == msg_recv['PLAYER']:
                    print 'sending %s to %s' % (msg, str(player[1]))
                    sock.sendto(json.dumps(msg), player[1])


def heart_beat(ip, port):
    print 'here'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = {'SERVER': ip, 'ACTION':'HEARTBEAT'}
    while True:
        sleep(2)
        players = []
        while not player_queue.empty():
            players.append(player_queue.get())
        for player in players:
            player_queue.put(player)
            print 'BEAT: %s' % (str(player[1]))
            sock.sendto(json.dumps(msg), player[1])


def main():
    ip = '127.0.0.1'
    #ip = '172.31.24.8'
    port = 56565
    threading.Thread(target=listen, args=(ip, port)).start()
    threading.Thread(target=heart_beat, args=(ip, port)).start()


main()