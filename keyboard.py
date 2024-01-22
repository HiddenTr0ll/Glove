import numpy as np
import settings
from settings import *
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from key import *
import pyrr
import midi  # https://github.com/vishnubob/python-midi

OCTAVES = 3


class Keyboard():
    def __init__(self):
        self.pattern = None
        self.track = None
        self.lastTick = 0
        #                         x, y, z
        self.position = np.array([-10, 55, 0], dtype=np.float32)
        self.keys: list[Key] = []
        self.keyPressed = {}

        for i in range(OCTAVES):
            position = 0
            for j in range(12):
                if j in midi.WHITE_KEYS:
                    self.keys.append(Key(self.position+np.array([i*7*2.2 + position * 2.2, 0, 0], dtype=np.float32), "white"))
                    position += 1
                else:
                    self.keys.append(Key(self.position+np.array([i*7*2.2 + position * 2.2 - 1.1, 0, 2], dtype=np.float32), "black"))

    def update(self, rate):
        for key in self.keys:
            key.update(rate)

    def draw(self):
        for key in self.keys:
            if (key.color == "white"):
                settings.whiteT.use()
            else:
                settings.blackT.use()
            glBindVertexArray(key.vao)
            glUniformMatrix4fv(
                settings.modelMatrixLocation, 1, GL_FALSE,
                key.get_model_transform())
            glDrawArrays(GL_TRIANGLES, 0, key.vertexCount)

    def updatePressed(self, pressedWhite):
        # set(new) ^ set(old) XOR?
        # toRelease = self.keyPressed - pressedWhite
        # toPress = pressedWhite - self.keyPressed
        # self.keyPressed = pressedWhite

        for index, key in enumerate(self.keyPressed):
            if index in pressedWhite:
                if not key.isPressed:
                    key.press()
                    self.record(True, index)
            else:
                if key.isPressed:
                    key.release()
                    self.record(False, index)

    def startRecording(self):
        settings.recording = True
        self.pattern = midi.Pattern()
        self.track = midi.Track()
        self.pattern.append(self.track)
        self.lastTick = glfw.get_time()
        pass

    def stopRecording(self):
        settings.recording = False
        eot = midi.EndOfTrackEvent(tick=1)
        self.track.append(eot)
        print(self.pattern)

    def record(self, pressed, keyIndex):

        if settings.recording:
            if self.pattern is not None:

                delta = glfw.get_time() - self.lastTick
                on = midi.NoteOnEvent(tick=delta, velocity=20, pitch=midi.G_3)
                self.track.append(on)

                off = midi.NoteOffEvent(tick=delta, pitch=midi.G_3)
                self.track.append(off)

        pass
