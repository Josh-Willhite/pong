from Tkinter import *
import random
import threading
from math import *
from Queue import Queue
import socket
import json

q = Queue()
#server_address = '54.86.251.5'
server_address = '127.0.0.1'
server_port = 56565


class Pong():
    def __init__(self, side):
        self.side = side
        self.player_name = 'default'
        self.game_started = False
        self.opponent_list = ''
        self.left_score = 0
        self.right_score = 0
        self.msg_number = 0
        self.opponent_ip = '127.0.0.1'
        self.opponent_port = 55555
        self.height = 200
        self.width = 400
        self.speed = 20
        self.paddle_height = self.height/4
        self.paddle_width = self.width/40
        self.ball_radius = self.width/40
        self.ball_color = 'red'
        self.paddle_color = 'green'
        self.ball_pos = [self.width/2, self.height/2]
        self.left_paddle_pos = self.height/2
        self.right_paddle_pos = self.height/2
        self.ball_angle = None

        self.root = Tk()
        self.command_line_in = Entry(self.root, width=60)
        self.command_line_out = Entry(self.root, width=60)
        self.window = Canvas(self.root, width=self.width, height=self.height)
        self.window.pack()
        self.command_line_in.insert(0, '>')
        self.command_line_in.pack()
        self.command_line_out.pack()
        self.command_line_in.bind('<Key>', self.key_event)
        self.window.bind_all('<Key>', self.key_event)
        self.ball = self.window.create_oval(self.width/2 - self.ball_radius, self.height/2 + self.ball_radius,
                                            self.width/2 + self.ball_radius, self.height/2 - self.ball_radius,
                                            fill=self.ball_color)

        self.left_paddle = self.window.create_rectangle(4, self.height/2 + self.paddle_height/2, 4 + self.paddle_width,
                                                       self.height/2 - self.paddle_height/2, fill=self.paddle_color)

        self.right_paddle = self.window.create_rectangle(self.width - self.paddle_width, self.height/2 + self.paddle_height/2,
                                                       self.width, self.height/2 - self.paddle_height/2, fill=self.paddle_color)

        self.update_game_state()
        self.send_game_state()
        self.check_queue()
        self.root.mainloop()

    def send_game_state(self):
        if self.game_started:
            msg = {}
            msg['PLAYER'] = self.player_name
            msg['ACTION'] = 'UPDATE'
            if self.side == 'left':
                msg['BPos'] = [self.ball_pos[0], self.ball_pos[1]]
                msg['BDir'] = self.ball_angle
                msg['PPos'] = self.left_paddle_pos
                msg['Goals'] = self.left_score
            else:
                msg['PPos'] = self.right_paddle_pos
                msg['Goals'] = self.right_score
            msg['UNum'] = self.msg_number
            self.udp_send(self.opponent_ip, self.opponent_port, json.dumps(msg))
            self.msg_number += 1
        self.root.after(100, self.send_game_state)

    def udp_send(self, ip, port, msg):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print 'SENDING %s %s %s' % (ip, port, msg)
        sock.sendto(msg, (ip, port))

    def chat(self, command):
        msg = {}
        msg['PLAYER'] = self.player_name
        msg['ACTION'] = 'CHAT'
        msg['MSG'] = ' '.join(command[2:])

        addr = None
        for op in self.opponent_list:
            if op[0] == command[1]:
                addr = op[1]

        if type(addr) == type(None):
            self.command_line_out.delete(0, END)
            self.command_line_out.insert(0, 'unable to find oppend in list')
        else:
            self.udp_send(addr[0], addr[1], json.dumps(msg))


    def check_queue(self):
        while not q.empty():
            msg = json.loads(q.get())
            print msg
            if 'PLAYER' in msg:
                if msg['ACTION'] == 'UPDATE':
                    if self.side == 'right':
                        self.ball_pos = [int(msg['BPos'][0]), int(msg['BPos'][1])]
                        self.left_paddle_pos = int(msg['PPos'])
                    else:
                        self.right_paddle_pos = int(msg['PPos'])
                if msg['ACTION'] == 'CHAT':
                    self.command_line_out.delete(0, END)
                    self.command_line_out.insert(0,msg['PLAYER'] + ' says: ' + msg['MSG'])

            elif 'SERVER' in msg:
                if msg['ACTION'] == 'LIST':
                    self.opponent_list = msg['OPPONENTS']
                    opponents = ''
                    for ops in self.opponent_list:
                        opponents += ops[0] + " "
                    self.command_line_out.delete(0, END)
                    self.command_line_out.insert(0, opponents)
                if msg['ACTION'] == 'HEARTBEAT':
                    #this is for debug only
                    #self.command_line_out.delete(0, END)
                    #self.command_line_out.insert(0, "BEAT")
                    print 'BEAT'

        self.root.after(1, self.check_queue)

    def listen(self, ip, port):
        msg = {'PLAYER':self.player_name, 'ACTION':'ADD'}
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(msg), (server_address, server_port))
        while True:
            data, addr = sock.recvfrom(1024)
            print addr
            print data
            q.put(data)

    def get_opponent_list(self):
        msg = {}
        msg['PLAYER'] = self.player_name
        msg['ACTION'] = 'LIST'
        self.udp_send(server_address, server_port, json.dumps(msg))

    def start_listener(self):
        listen = threading.Thread(target=self.listen, args=('127.0.0.1', 55556))
        listen.setDaemon(True)
        listen.start()

    def command_interpreter(self):
        commands = ['>msg', '>quit', '>list', '>set_name', '>start_game', '>start_listener']
        command = self.command_line_in.get().split(' ')
        if command[0] in commands:
            if command[0] == '>msg':
                self.chat(command)
                self.command_line_out.delete(0, END)
                self.command_line_out.insert(0, 'sending message ...')
            if command[0] == '>start_listener':
                if self.player_name != 'default':
                    self.start_listener()
                    self.command_line_out.delete(0, END)
                    self.command_line_out.insert(0,'registered with server and listening')
                else:
                    self.command_line_out.delete(0, END)
                    self.command_line_out.insert(0, 'Please "set_name" before registering')
            if command[0] == '>start_game':
                self.game_started = True
                self.command_line_out.delete(0, END)
                self.command_line_out.insert(0,'game started!')
            if command[0] == '>quit':
                self.root.quit()
            if command[0] == '>list':
                self.get_opponent_list()
            if command[0] == '>set_name':
                self.player_name = command[1]
                self.command_line_out.delete(0, END)
                self.command_line_out.insert(0,'your player name is: "' + self.player_name + '"')

            self.command_line_in.delete(0, END)
            self.command_line_in.insert(0, '>')

        elif command[0] != '>':
            self.command_line_in.delete(0, END)
            self.command_line_in.insert(0, '>')
            self.command_line_out.delete(0, END)
            self.command_line_out.insert(0,'ERROR: "' + str(command) + '" not recognized')

    def key_event(self, event):
        if event.keysym == 'Return':
            self.command_interpreter()
        if self.game_started:
            if self.side == 'left':
                if event.keysym == 'Up':
                    if self.left_paddle_pos > self.paddle_height/2:
                        self.left_paddle_pos -= self.height/20
                        self.window.move(self.left_paddle, 0, -self.height/20)
                        return "break"
                if event.keysym == 'Down':
                    if self.left_paddle_pos < self.height - self.paddle_height/2:
                        self.left_paddle_pos += self.height/20
                        self.window.move(self.left_paddle, 0, self.height/20)
                        return "break"
            else:
                if event.keysym == 'Up':
                    if self.right_paddle_pos > self.paddle_height/2:
                        self.right_paddle_pos -= self.height/20
                        self.window.move(self.right_paddle, 0, -self.height/20)
                        return "break"
                if event.keysym == 'Down':
                    if self.right_paddle_pos < self.height - self.paddle_height/2:
                        self.right_paddle_pos += self.height/20
                        self.window.move(self.right_paddle, 0, self.height/20)
                        return "break"
        else:
            if event.keysym in {'Up', 'Down'}:
                return 'break'

    def update_game_state(self):
        if self.game_started:
            if self.side == 'left':
                self.next_ball_position()

            self.window.coords(self.ball, self.ball_pos[0] - self.ball_radius, self.ball_pos[1] + self.ball_radius,
                                            self.ball_pos[0] + self.ball_radius, self.ball_pos[1] - self.ball_radius)
            if self.side == 'left':
                self.window.coords(self.right_paddle, self.width - self.paddle_width, self.right_paddle_pos + self.paddle_height/2,
                                                           self.width, self.right_paddle_pos - self.paddle_height/2)
            else:
                self.window.coords(self.left_paddle, 4, self.left_paddle_pos + self.paddle_height/2, 4 + self.paddle_width,
                                                       self.left_paddle_pos - self.paddle_height/2)
            self.root.after(self.speed, self.update_game_state)

    def next_ball_position(self):
        if type(self.ball_angle) == type(None):
            self.ball_angle = random.choice([random.choice([x for x in range(0, 70)]), random.choice([x for x in range(110, 250)]),
                                        random.choice([x for x in range(290,359)])])
        #LEFT
        if self.ball_pos[0] < 0:
            #check to see if paddle is in the way
            if self.ball_pos[1] < (self.left_paddle_pos + self.paddle_height/2)  and self.ball_pos[1] > (self.left_paddle_pos - self.paddle_height/2):
                if self.ball_angle < 180:
                    self.ball_angle = 90 - (self.ball_angle - 90)
                else:
                    self.ball_angle = 180 - self.ball_angle
        #RIGHT
        elif self.ball_pos[0] > self.width:
            #if self.curr_pos[1] < (self.right_paddle_pos + self.paddle_height/2)  and self.curr_pos[1] > (self.right_paddle_pos - self.paddle_height/2):
                if self.ball_angle < 90:
                    self.ball_angle = 180 - self.ball_angle
                else:
                    self.ball_angle = 360 - self.ball_angle
        #TOP
        elif self.ball_pos[1] < 0:
            self.ball_angle = 360 - self.ball_angle
        #BOTTOM
        #TODO fix bounce behavior off bottom
        elif self.ball_pos[1] > self.height:
            if self.ball_angle > 270:
                self.ball_angle = 360 - self.ball_angle
            else:
                self.ball_angle = 180 - (270 - self.ball_angle)

        self.ball_pos = [cos(radians(self.ball_angle)) + self.ball_pos[0], - sin(radians(self.ball_angle)) + self.ball_pos[1]]





if __name__ == "__main__":
    Pong('left')
