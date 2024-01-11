from __future__ import annotations

import numpy as np
import pyrr

from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403

# TODO change Limb to Entity -> create keyboard


class Cuboid():
    def __init__(self):
        self.rotation = pyrr.matrix44.create_identity()
        self.genVertices(self.l, self.w, self.h)
        self.createBuffers()

    def genVertices(self, l, w, h):
        # x,y,z , s,t
        self.vertices = (
            -l/2, -w/2, 0, 0, 0,
            l/2, -w/2, 0, 1, 0,
            l/2,  w/2, 0, 1, 1,

            l/2,  w/2, 0, 1, 1,
            -l/2,  w/2, 0, 0, 1,
            -l/2, -w/2, 0, 0, 0,

            -l/2, -w/2,  h, 0, 0,
            l/2, -w/2,  h, 1, 0,
            l/2,  w/2,  h, 1, 1,

            l/2,  w/2,  h, 1, 1,
            -l/2,  w/2,  h, 0, 1,
            -l/2, -w/2,  h, 0, 0,

            -l/2,  w/2,  h, 1, 0,
            -l/2,  w/2, 0, 1, 1,
            -l/2, -w/2, 0, 0, 1,

            -l/2, -w/2, 0, 0, 1,
            -l/2, -w/2,  h, 0, 0,
            -l/2,  w/2,  h, 1, 0,

            l/2,  w/2,  h, 1, 0,
            l/2,  w/2, 0, 1, 1,
            l/2, -w/2, 0, 0, 1,

            l/2, -w/2, 0, 0, 1,
            l/2, -w/2,  h, 0, 0,
            l/2,  w/2,  h, 1, 0,

            -l/2, -w/2, 0, 0, 1,
            l/2, -w/2, 0, 1, 1,
            l/2, -w/2,  h, 1, 0,

            l/2, -w/2,  h, 1, 0,
            -l/2, -w/2,  h, 0, 0,
            -l/2, -w/2, 0, 0, 1,

            -l/2,  w/2, 0, 0, 1,
            l/2,  w/2, 0, 1, 1,
            l/2,  w/2,  h, 1, 0,

            l/2,  w/2,  h, 1, 0,
            -l/2,  w/2,  h, 0, 0,
            -l/2,  w/2, 0, 0, 1
        )
        self.verticesArray = np.array(self.vertices, dtype=np.float32)
        self.vertexCount = 36

    def createBuffers(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.verticesArray.nbytes, self.verticesArray, GL_STATIC_DRAW)

        # vertexArrayPointer format:
        # index, size, type, legacy, stride (2x3x4 Byte), offset

        glEnableVertexAttribArray(0)  # position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)  # texcoord
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))

    def overlapsWith(self, other: "Limb"):
        # x
        if (self.position[0]-self.l/2) > (other.position[0]+other.l/2):
            return False

        if (self.position[0]+self.l/2) < (other.position[0]-other.l/2):
            return False

        # y
        if (self.position[1]-self.w/2) > (other.position[1]+other.w/2):
            return False

        if (self.position[1]+self.w/2) < (other.position[1]-other.w/2):
            return False

        # z
        if (self.position[2]) > (other.position[2]+other.h):
            return False

        if (self.position[2]+self.h) < (other.position[2]):
            return False

        return True

    def updateRotation(self, rotation):
        self.rotation = rotation

    def updatePosition(self, position):
        self.position = position

    def get_model_transform(self) -> np.ndarray:
        """
            Returns the entity's model to world
            transformation matrix.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=self.rotation
        )

        return pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position), dtype=np.float32
            )
        )

    # saved code vor keyboard animation

    """
    def update(self, rate):
        
        # TODO: update rotation from settings

        self.eulers[2] += 0.2 * rate

        if self.eulers[2] > 360:
            self.eulers[2] -= 360

        self.eulers[0] += 0.2 * rate

        if self.eulers[0] > 360:
            self.eulers[0] -= 360

        self.updateRotation(pyrr.matrix44.create_from_eulers(
            eulers=np.radians(self.eulers),
            dtype=np.float32))
        self.calculateTip()
        """
