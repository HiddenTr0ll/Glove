from settings import *
import settings
from arm import Arm
from keyboard import Keyboard
import pyrr


class Scene:

    def __init__(self):
        # init all arms and keyboard here
        self.camPos = np.array([0, -100, 20], dtype=np.float32)
        self.camTheta = 90
        self.camPhi = 0
        self.updateCameraVectors()
        self.arm1 = Arm()
        self.keyboard = Keyboard()

    def moveCamera(self, dPos):
        dPos = np.array(dPos, dtype=np.float32)
        self.camPos += dPos

    def spinCamera(self, dTheta, dPhi):
        self.camTheta += dTheta
        self.camPhi += dPhi
        if self.camTheta > 360:
            self.camTheta -= 360
        elif self.camTheta < 0:
            self.camTheta += 360

        self.camPhi = min(
            89, max(-89, self.camPhi + dPhi)
        )
        self.updateCameraVectors()

    def updateCameraVectors(self):
        self.forwards = np.array([
            np.cos(np.deg2rad(self.camTheta))*np.cos(np.deg2rad(self.camPhi)),
            np.sin(np.deg2rad(self.camTheta))*np.cos(np.deg2rad(self.camPhi)),
            np.sin(np.deg2rad(self.camPhi))
        ])

        globalUp = np.array([0, 0, 1], dtype=np.float32)

        # right is perpendicular to forwards and up! -> right hand point forward, curl fingers up -> thumb pointing right!
        self.right = np.cross(self.forwards, globalUp)

        # finger pointing right, curling forwards -> thumbs points up!
        self.up = np.cross(self.right, self.forwards)

    def update(self, rate):
        # TODO: update arm and finger rotations/positions
        # settings.arm1.finger1.update(rate)
        # settings.arm1.finger2.update(rate)
        # settings.arm1.spin(rate)
        self.arm1.update()
        pass

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(settings.shader)

        viewTransform = pyrr.matrix44.create_look_at(
            eye=self.camPos,
            target=self.camPos+self.forwards,
            up=self.up,
            dtype=np.float32
        )
        glUniformMatrix4fv(settings.viewMatrixLocation, 1, GL_FALSE, viewTransform)

        self.arm1.draw()
        self.keyboard.draw()
        glFlush()

    def quit(self):
        glDeleteVertexArrays(len(self.arm1.limbs), [o.vao for o in self.arm1.limbs])
        glDeleteVertexArrays(len(self.keyboard.keys), [o.vao for o in self.keyboard.keys])
