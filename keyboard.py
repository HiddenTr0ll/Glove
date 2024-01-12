import numpy as np
import settings
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from key import *
import pyrr

OCTAVES = 3


class Keyboard():
    def __init__(self):
        #                         x, y, z
        self.position = np.array([-10, 55, 0], dtype=np.float32)
        self.whiteKeys: list[Key] = []
        self.blackKeys: list[Key] = []
        for i in range(OCTAVES*7):
            self.whiteKeys.append(Key(self.position+np.array([i*2.2, 0, 0], dtype=np.float32), "white"))
            if (i % 7 == 0) or (i % 7 == 3):
                continue
            self.blackKeys.append(Key(self.position+np.array([i*2.2 - 1.1, 0, 2], dtype=np.float32), "black"))

    def update(self, rate):
        for key in self.whiteKeys:
            key.update(rate)
        for key in self.blackKeys:
            key.update(rate)

    def draw(self):
        settings.whiteT.use()
        for key in self.whiteKeys:
            glBindVertexArray(key.vao)
            glUniformMatrix4fv(
                settings.modelMatrixLocation, 1, GL_FALSE,
                key.get_model_transform())
            glDrawArrays(GL_TRIANGLES, 0, key.vertexCount)

        settings.blackT.use()
        for key in self.blackKeys:
            glBindVertexArray(key.vao)
            glUniformMatrix4fv(
                settings.modelMatrixLocation, 1, GL_FALSE,
                key.get_model_transform())
            glDrawArrays(GL_TRIANGLES, 0, key.vertexCount)
