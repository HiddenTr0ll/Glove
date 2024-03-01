from numpy import ndarray
from cuboid import *
import settings


class Limb(Cuboid):
    def __init__(self, l, w, h):
        #                         x, y, z
        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.l = l
        self.w = w
        self.h = h
        self.rotation = pyrr.matrix44.create_identity()
        super().__init__()
        self.calculateTip()

    def calculateTip(self):
        delta = np.dot(np.array([0, 0, self.h, 0], dtype=np.float32), self.rotation)
        self.tipPosition = self.position + delta[:3]

    def calculateFingerTip(self):
        delta = np.dot(np.array([0, 0, self.h - (self.l+self.b)/2, 0], dtype=np.float32), self.rotation)
        self.tipPosition = self.position + delta[:3]

    def get_hand_model_transform(self):
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=self.rotation
        )

        # translate to relative hand positions
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position), dtype=np.float32
            )
        )

        # rotate arround axis
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_axis_rotation(
                axis=np.array([0, 0, -1]), theta=settings.armAngle, dtype=np.float32
            )
        )

        # translate to absolute world position
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(settings.armPos), dtype=np.float32
            )
        )

        return model_transform

    def draw(self):
        glBindVertexArray(self.vao)
        glUniformMatrix4fv(
            settings.modelMatrixLocation, 1, GL_FALSE,
            self.get_hand_model_transform())
        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)
