import socket
import json
import threading
from time import time
from time import sleep
from Queue import Queue

player_queue = Queue()


def listen(ip, port):
    print 'listening:%s:%s' % (str(ip), str(port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    while True:
        data, addr = sock.recvfrom(1024)
        msg_recv = json.loads(data)
        print msg_recv
        players = []

        #get players from queue
        while not player_queue.empty():
                players.append(player_queue.get())

        if msg_recv['ACTION'] == 'ADD':
            entry = [msg_recv['PLAYER'], addr, time()]
            player_queue.put(entry)

        if msg_recv['ACTION'] == 'REMOVE':
            for player in players:
                if player[0] == msg_recv['PLAYER']:
                    players.remove(player)

        if msg_recv['ACTION'] == 'BEAT':
            #update players time
            for player in players:
                if player[0] == msg_recv['PLAYER']:
                    player[2] = time()

        if msg_recv['ACTION'] == 'LIST':
            msg = {'SERVER':ip, 'ACTION':'LIST', 'OPPONENTS':players}
            for player in players:
                if player[0] == msg_recv['PLAYER']:
                    print 'sending %s to %s' % (msg, str(player[1]))
                    sock.sendto(json.dumps(msg), player[1])

        #put players back on queue
        curr_time = time()
        for player in players:
            if curr_time - player[2] < 10:
                player_queue.put(player)
            else:
                print 'player %s retired due to timeout' % player[0]

def heart_beat(ip, port):
    print 'here'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = {'SERVER': ip, 'ACTION':'HEARTBEAT'}
    while True:
        sleep(1)
        players = []
        while not player_queue.empty():
            players.append(player_queue.get())
        for player in players:
            player_queue.put(player)
            print 'BEAT: %s' % (str(player[1]))
            sock.sendto(json.dumps(msg), player[1])


def main():
    #ip = '127.0.0.1'
    #ip = '172.31.24.8'
    ip = '192.168.1.135'
    port = 56565
    threading.Thread(target=listen, args=(ip, port)).start()
    threading.Thread(target=heart_beat, args=(ip, port)).start()

main()