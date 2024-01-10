import numpy as np
import settings
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from limb import Limb
import pyrr


class Arm():
    def __init__(self):
        self.needsUpdate = True
        self.indexShift = [0, 6, 1, 2, 3, 4, 5]
        self.limbs = [Limb(index=self.indexShift[i], l=1, w=1, h=3) for i in range(7)]
        for f in self.limbs:
            print(f.index)

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
        if all([np.allclose(x, y, atol=0.0001) for x, y in zip(self.rotationList, settings.rotationList)]) | self.needsUpdate:
            self.rotationList = settings.rotationList
            self.updateAngles()
            self.updatePositions()
            # self.needsUpdate = False

    def updateAngles(self):
        for index, limb in enumerate(self.limbs):
            limb.updateRotation(self.rotationList[self.indexShift[index]])

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
