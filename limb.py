from __future__ import annotations

import numpy as np
import pyrr

import settings

from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403


class Limb():
    def __init__(self, index, l, w, h):
        self.index = index
        #                         x, y, z
        self.position = np.array([index*2, 4, 0], dtype=np.float32)
        self.eulers = np.array([0, 0, 0], dtype=np.float32)
        self.rotation = pyrr.matrix44.create_from_eulers(
            eulers=np.radians(self.eulers),
            dtype=np.float32)

        self.l = l
        self.w = w
        self.h = h
        self.tipPosition = self.calculateTip()
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

    def update(self, rate):
        """
            Update the object, this is hard coded for now.
        """
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

    def updateRotation(self, rotation):
        self.rotation = rotation

    def updatePosition(self, pos):
        self.position = pos
        self.calculateTip()

    def calculateTip(self):
        # TODO: calculate tip position
        # print(self.rotation)
        delta = np.dot(np.array([0, 0, 1, 0], dtype=np.float32), self.rotation) * self.h

        self.tipPosition = self.position + delta[:3]

        # print(tip)

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
