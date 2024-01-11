from cuboid import *


class Key(Cuboid):
    def __init__(self, position, color):
        #                         x, y, z 2,2 15 2
        self.position = position
        self.color = color
        if (color == "white"):
            self.l = 2.0
            self.w = 15.0
            self.h = 2.0
        elif (color == "black"):
            self.l = 1.0
            self.w = 9.0
            self.h = 1.0
        super().__init__()
