from Tkinter import *
import random
import threading
from math import *


class Pong(threading.Thread):
    def __init__(self, side):
        self.side = side
        self.height = 200
        self.width = 400
        self.speed = 20
        self.paddle_height = self.height/4
        self.paddle_width = self.width/40
        self.ball_radius = self.width/40
        self.ball_color = 'red'
        self.paddle_color = 'green'
        self.root = Tk()
        self.window = Canvas(self.root, width=self.width, height=self.height)
        self.curr_pos = [self.width/2, self.height/2]
        self.prev_pos = [self.width/2, self.height/2]
        self.left_paddle_pos = self.height/2
        self.right_paddle_pos = self.height/2
        self.angle = 0
        self.window.pack()
        self.window.bind_all('<Key>', self.key_event)
        self.ball = self.window.create_oval(self.width/2 - self.ball_radius, self.height/2 + self.ball_radius,
                                            self.width/2 + self.ball_radius, self.height/2 - self.ball_radius, fill=self.ball_color)

        self.left_paddle = self.window.create_rectangle(4, self.height/2 + self.paddle_height/2, 4 + self.paddle_width,
                                                       self.height/2 - self.paddle_height/2, fill=self.paddle_color)

        self.right_paddle = self.window.create_rectangle(self.width - self.paddle_width, self.height/2 + self.paddle_height/2,
                                                       self.width, self.height/2 - self.paddle_height/2, fill=self.paddle_color)
        self.update_ball_position()
        #threading.Thread.__init__(self)
        self.root.mainloop()

    #def run(self):
    #    self.root.mainloop()

    def update_state(self, left_paddle, ball, right_paddle):

        return None

    def key_event(self, event):
        if self.side == 'left':
            paddle = self.left_paddle
        else:
            paddle = self.right_paddle

        if event.keysym == 'Up':
            if self.left_paddle_pos > self.paddle_height/2:
                self.left_paddle_pos -= self.height/20
                self.window.move(paddle, 0, -self.height/20)
        if event.keysym == 'Down':
            if self.left_paddle_pos < self.height - self.paddle_height/2:
                self.left_paddle_pos += self.height/20
                self.window.move(paddle, 0, self.height/20)

    def update_ball_position(self):
        self.next_position()
        self.window.coords(self.ball, self.curr_pos[0] - self.ball_radius, self.curr_pos[1] + self.ball_radius,
                                            self.curr_pos[0] + self.ball_radius, self.curr_pos[1] - self.ball_radius)
        self.root.after(self.speed, self.update_ball_position)
        return False

    def next_position(self):
        if self.curr_pos == self.prev_pos:
            self.angle = random.choice([random.choice([x for x in range(0, 70)]), random.choice([x for x in range(110, 250)]),
                                        random.choice([x for x in range(290,359)])])

        self.prev_pos = self.curr_pos
        #LEFT
        if self.prev_pos[0] < 0:
            #check to see if paddle is in the way
            if self.curr_pos[1] < (self.left_paddle_pos + self.paddle_height/2)  and self.curr_pos[1] > (self.left_paddle_pos - self.paddle_height/2):
                if self.angle < 180:
                    self.angle = 90 - (self.angle - 90)
                else:
                    self.angle = 180 - self.angle
        #RIGHT
        elif self.prev_pos[0] > self.width:
            if self.curr_pos[1] < (self.right_paddle_pos + self.paddle_height/2)  and self.curr_pos[1] > (self.right_paddle_pos - self.paddle_height/2):
                if self.angle < 90:
                    self.angle = 180 - self.angle
                else:
                    self.angle = 360 - self.angle
        #TOP
        elif self.prev_pos[1] < 0:
            self.angle = 360 - self.angle
        #BOTTOM
        #TODO fix bounce behavior off bottom
        elif self.prev_pos[1] > self.height:
            if self.angle > 270:
                self.angle = 360 - self.angle
            else:
                self.angle = 180 - (270 - self.angle)

        self.curr_pos = [cos(radians(self.angle)) + self.prev_pos[0], - sin(radians(self.angle)) + self.prev_pos[1]]


if __name__ == "__main__":
    app = Pong('left')
    app.start()