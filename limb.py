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
        self.tipPosition = self.calculateTip()

    def calculateTip(self):
        delta = np.dot(np.array([0, 0, self.h, 0], dtype=np.float32), self.rotation)
        self.tipPosition = self.position + delta[:3]

    def updatePositionWithOffset(self, palmTip, palmRotation, offsetX, offsetZ):
        delta = np.dot(np.array([offsetX, 0, offsetZ], dtype=np.float32), palmRotation[:3, :3])
        self.position = palmTip + delta

    def draw(self):
        glBindVertexArray(self.vao)
        glUniformMatrix4fv(
            settings.modelMatrixLocation, 1, GL_FALSE,
            self.get_model_transform())
        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)
