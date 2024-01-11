import numpy as np
import settings
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from key import *
import pyrr


class Keyboard():
    def __init__(self):
        #                         x, y, z
        self.position = np.array([-50, 50, 0], dtype=np.float32)
        self.whiteKeys = [Key(self.position+np.array([i*2.2, 0, 0], dtype=np.float32), "white") for i in range(55)]
        self.blackKeys = []
        for i in range(55):
            if (i % 7 == 0) or (i % 7 == 3):
                continue
            self.blackKeys.append(Key(self.position+np.array([i*2.2 - 1.1, 0, 2], dtype=np.float32), "black"))

    def spin(self, rate):
        for limb in self.limbs:
            limb.update(rate)
        self.needsUpdate = True
        self.update()

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
