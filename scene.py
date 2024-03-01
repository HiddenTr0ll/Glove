from settings import *
import settings
from arm import Arm
from keyboard import Keyboard
import pyrr


class Scene:

    def __init__(self):
        # init all arms and keyboard here
        self.updateCameraVectors()
        self.arm1 = Arm()
        self.keyboard = Keyboard()

    def moveCamera(self, dPos):
        dPos = np.array(dPos, dtype=np.float32)
        settings.camPos += dPos

    def spinCamera(self, dTheta, dPhi):
        settings.camTheta += dTheta
        settings.camPhi += dPhi
        if settings.camTheta > 360:
            settings.camTheta -= 360
        elif settings.camTheta < 0:
            settings.camTheta += 360

        settings.camPhi = min(
            89, max(-89, settings.camPhi + dPhi)
        )
        self.updateCameraVectors()

    def updateCameraVectors(self):
        self.forwards = np.array([
            np.cos(np.deg2rad(settings.camTheta))*np.cos(np.deg2rad(settings.camPhi)),
            np.sin(np.deg2rad(settings.camTheta))*np.cos(np.deg2rad(settings.camPhi)),
            np.sin(np.deg2rad(settings.camPhi))
        ])

        globalUp = np.array([0, 0, 1], dtype=np.float32)

        # right is perpendicular to forwards and up! -> right hand point forward, curl fingers up -> thumb pointing right!
        self.right = np.cross(self.forwards, globalUp)

        # finger pointing right, curling forwards -> thumbs points up!
        self.up = np.cross(self.right, self.forwards)

    def update(self, rate):
        self.arm1.update()
        overlap = self.arm1.overlapsWith(self.keyboard.keys)
        self.keyboard.updatePressed(set(overlap))
        self.keyboard.update(rate)
        pass

    def render(self):

        glUseProgram(settings.shader)

        viewTransform = pyrr.matrix44.create_look_at(
            eye=settings.camPos,
            target=settings.camPos+self.forwards,
            up=self.up,
            dtype=np.float32
        )
        glUniformMatrix4fv(settings.viewMatrixLocation, 1, GL_FALSE, viewTransform)

        self.arm1.draw()
        self.keyboard.draw()

    def quit(self):
        self.arm1.destroy()
        self.keyboard.destroy()
