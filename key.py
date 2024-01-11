from cuboid import *


class Key(Cuboid):
    def __init__(self, position, color):
        #                         x, y, z
        self.position = position
        self.color = color
        if (color == "white"):
            self.l = 1
            self.w = 1
            self.h = 1
        elif (color == "black"):
            self.l = 1
            self.w = 1
            self.h = 1
        super().__init__()
