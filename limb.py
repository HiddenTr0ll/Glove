from cuboid import *


class Limb(Cuboid):
    def __init__(self, l, w, h):

        self.l = l
        self.w = w
        self.h = h

        super().__init__()
        self.tipPosition = self.calculateTip()

    def calculateTip(self):
        delta = np.dot(np.array([0, 0, self.h, 0], dtype=np.float32), self.rotation)
        self.tipPosition = self.position + delta[:3]

    def updatePositionWithOffset(self, palmTip, palmRotation, offsetX, offsetZ):
        delta = np.dot(np.array([offsetX, 0, offsetZ], dtype=np.float32), palmRotation[:3, :3])
        self.position = palmTip + delta
