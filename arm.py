import numpy as np
import settings

from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from limb import Limb


class Arm():
    def __init__(self):
        self.limbs = [Limb(l=2, w=1, h=3) for _ in range(1)]
        self.indexShift = [0, 6, 1, 2, 3, 4, 5]
        self.rotationList = settings.rotationList
        # self.finger2 = Limb(l=1, w=1, h=2)
        # self.update()
        # for i in range(1):
        #   self.limbs[i].updatePosition(np.array([2, 0, 0], dtype=np.float32))

    def spin(self, rate):
        for limb in self.limbs:
            limb.update(rate)

    def update(self):
        if self.rotation != settings.rotation:
            self.rotation = settings.rotation
            self.updateAngles()
            self.updatePositions()

    def updateAngles(self):
        for index, limb in enumerate(self.limbs):
            limb.updateRotation(self.rotation[self.indexShift[index]])

    def updatePositions(self):
        self.limbs[0].calculateTip()
        self.limbs[6].updatePosition(self.limbs[0].tipPosition)
        for i in range(1, 6):
            self.limbs[i].updatePosition(self.limbs[6].tipPosition)

    def draw(self):
        settings.texture.use()
        for limb in self.limbs:
            glBindVertexArray(limb.vao)
            glUniformMatrix4fv(
                settings.modelMatrixLocation, 1, GL_FALSE,
                limb.get_model_transform())
            glDrawArrays(GL_TRIANGLES, 0, limb.vertexCount)
