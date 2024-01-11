import numpy as np
import settings
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from key import *
import pyrr


class keyboard():
    def __init__(self):
        self.keys = [Key("white") for i in range(7)]

    def spin(self, rate):
        for limb in self.limbs:
            limb.update(rate)
        self.needsUpdate = True
        self.update()

    def draw(self):
        settings.texture.use()
        for key in self.keys:
            glBindVertexArray(key.vao)
            glUniformMatrix4fv(
                settings.modelMatrixLocation, 1, GL_FALSE,
                key.get_model_transform())
            glDrawArrays(GL_TRIANGLES, 0, key.vertexCount)
