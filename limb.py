from cuboid import *


class Limb(Cuboid):
    def __init__(self, l, w, h):
        #                         x, y, z
        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.l = l
        self.w = w
        self.h = h
        self.rotation = pyrr.matrix44.create_identity()
        super().__init__()
        self.tipPosition = self.calculateTip()

    def calculateTip(self):
        delta = np.dot(np.array([0, 0, self.h, 0], dtype=np.float32), self.rotation)
        self.tipPosition = self.position + delta[:3]

    def updatePositionWithOffset(self, palmTip, palmRotation, offsetX, offsetZ):
        delta = np.dot(np.array([offsetX, 0, offsetZ], dtype=np.float32), palmRotation[:3, :3])
        self.position = palmTip + delta

    def overlapsWith(self, cubeList: list[Cuboid]):
        self.calculateTip()
        overlapping = []
        for index, cube in enumerate(cubeList):
            # x
            if (self.tipPosition[0]+self.l/2) < (cube.position[0]-cube.l/2):
                continue

            if (self.tipPosition[0]-self.l/2) > (cube.position[0]+cube.l/2):
                continue

            # y
            if (self.tipPosition[1]) < (cube.position[1]-cube.h):
                continue

            if (self.tipPosition[1]-2) > (cube.position[1]):
                continue

            # z
            if (self.tipPosition[2]-self.w/2) > (cube.position[2]+cube.w/2):
                continue

            if (self.tipPosition[2]+self.w/2) < (cube.position[2]+cube.w/2):
                continue

            overlapping.append(index)
        return overlapping
