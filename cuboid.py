from __future__ import annotations

import numpy as np
import pyrr

from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403

# TODO change Limb to Entity -> create keyboard


class Cuboid():
    def __init__(self):

        self.b = 0.2
        self.genVertices(self.l, self.w, self.h, self.b)
        self.createBuffers()

    def genVertices(self, l, w, h, b):
        # x,y,z , s,t
        self.vertices = (  # -b/w
            -l/2, -w/2, 0, -b/l, -b/w,
            l/2, -w/2, 0, 1+b/l, -b/w,
            l/2,  w/2, 0, 1+b/l, 1+b/w,

            l/2,  w/2, 0, 1+b/l, 1+b/w,
            -l/2,  w/2, 0, -b/l, 1+b/w,
            -l/2, -w/2, 0, -b/l, -b/w,

            -l/2, -w/2,  h, -b/l, -b/w,
            l/2, -w/2,  h, 1+b/l, -b/w,
            l/2,  w/2,  h, 1+b/l, 1+b/w,

            l/2,  w/2,  h, 1+b/l, 1+b/w,
            -l/2,  w/2,  h, -b/l, 1+b/w,
            -l/2, -w/2,  h, -b/l, -b/w,

            -l/2,  w/2,  h, 1+b/l, -b/h,
            -l/2,  w/2, 0, 1+b/l, 1+b/h,
            -l/2, -w/2, 0, -b/l, 1+b/h,

            -l/2, -w/2, 0, -b/l, 1+b/h,
            -l/2, -w/2,  h, -b/l, -b/h,
            -l/2,  w/2,  h, 1+b/l, -b/h,

            l/2,  w/2,  h, 1+b/l, -b/h,
            l/2,  w/2, 0, 1+b/l, 1+b/h,
            l/2, -w/2, 0, -b/l, 1+b/h,

            l/2, -w/2, 0, -b/l, 1+b/h,
            l/2, -w/2,  h, -b/l, -b/h,
            l/2,  w/2,  h, 1+b/l, -b/h,

            -l/2, -w/2, 0, -b/l, 1+b/h,
            l/2, -w/2, 0, 1+b/l, 1+b/h,
            l/2, -w/2,  h, 1+b/l, -b/h,

            l/2, -w/2,  h, 1+b/l, -b/h,
            -l/2, -w/2,  h, -b/l, -b/h,
            -l/2, -w/2, 0, -b/l, 1+b/h,

            -l/2,  w/2, 0, -b/l, 1+b/h,
            l/2,  w/2, 0, 1+b/l, 1+b/h,
            l/2,  w/2,  h, 1+b/l, -b/h,

            l/2,  w/2,  h, 1+b/l, -b/h,
            -l/2,  w/2,  h, -b/l, -b/h,
            -l/2,  w/2, 0, -b/l, 1+b/h
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

        # position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # texcoord
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

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

    def destroy(self):
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))
