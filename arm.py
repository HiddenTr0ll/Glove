import numpy as np
import settings
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from limb import *
import pyrr


class Arm():
    def __init__(self):
        self.measurements = (
            # l, w, h,
            6.0, 5.0, 27.5,               # loweArm   0
            2.0, 1.7, 11.5,               # thumb     1
            1.7, 1.5, 9.5,                # index     2
            1.7, 1.6, 11.0,               # middle    3
            1.6, 1.5, 10.5,               # ring      4
            1.5, 1.3, 8.0,                # pinky     5
            8.5, 3.0, 8.5                 # palm      6
        )
        self.offsets = (
            -4.0, -2.8, -0.5, 1.4, 3.1,   # x-offset fingers
            -7.5, 0.0, 0.0, 0.0, 0.0       # y-offset thumb
        )
        self.limbs = [Limb(
            l=self.measurements[i*3],
            w=self.measurements[i*3+1],
            h=self.measurements[i*3+2]
        ) for i in range(7)]

        self.rotationList = settings.rotationList
        self.update()

    def spin(self, rate):
        for limb in self.limbs:
            limb.update(rate)
        self.needsUpdate = True
        self.update()

    def update(self):
        # zip: convert list to tubles of 2 arrays
        # allclose: compare if 2 arrays are euqual element wise with tolerance
        # all: OR combination of all truth values
        # if all([np.allclose(x, y, atol=0.0001) for x, y in zip(self.rotationList, settings.rotationList)]):
        self.rotationList = settings.rotationList
        self.updateAngles()
        self.updatePositions()

    def updateAngles(self):
        for index, limb in enumerate(self.limbs):
            limb.updateRotation(self.rotationList[index])

    def updatePositions(self):
        self.limbs[0].calculateTip()
        self.limbs[6].updatePosition(self.limbs[0].tipPosition)
        self.limbs[6].calculateTip()
        for i in range(1, 6):
            self.limbs[i].updatePositionWithOffset(
                self.limbs[6].tipPosition,
                self.limbs[6].rotation,
                self.offsets[i-1],
                self.offsets[i+4])

    def draw(self):
        settings.texture.use()
        for limb in self.limbs:
            glBindVertexArray(limb.vao)
            glUniformMatrix4fv(
                settings.modelMatrixLocation, 1, GL_FALSE,
                limb.get_model_transform())
            glDrawArrays(GL_TRIANGLES, 0, limb.vertexCount)
