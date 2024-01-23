import numpy as np
import settings
from settings import *
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from key import *
import pyrr
from mido import Message, MidiFile, MidiTrack

OCTAVES = 3


class Keyboard():
    def __init__(self):
        self.file = None
        self.track = None
        self.lastTick = 0
        #                         x, y, z
        self.position = np.array([-10, 55, 0], dtype=np.float32)
        self.keys: list[Key] = []
        self.keyPressed = set()

        for i in range(OCTAVES):
            position = 0
            for j in range(12):
                if j in [0, 2, 4, 5, 7, 9, 11]:  # whitekeys
                    self.keys.append(Key(self.position+np.array([i*7*2.2 + position * 2.2, 0, 0], dtype=np.float32), "white"))
                    position += 1
                else:
                    self.keys.append(Key(self.position+np.array([i*7*2.2 + position * 2.2 - 1.1, 0, 1.5], dtype=np.float32), "black"))

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

    def updatePressed(self, pressed):
        # set(new) ^ set(old) XOR?
        toRelease = self.keyPressed - pressed
        toPress = pressed - self.keyPressed
        self.keyPressed = pressed
        delta = int(1000*(glfw.get_time() - self.lastTick))
        print(delta)
        keyIndex: int
        for keyIndex in toPress:
            self.keys[keyIndex].press()
            if (settings.recording):
                self.record("note_on", keyIndex, delta)
        for keyIndex in toRelease:
            self.keys[keyIndex].release()
            if (settings.recording):
                self.record("note_off", keyIndex, delta)

        if len(toPress) != 0 or len(toRelease) != 0:
            self.lastTick = glfw.get_time()

    def startRecording(self):
        if not settings.recording:
            self.file = MidiFile()
            self.track = MidiTrack()
            self.file.tracks.append(self.track)

            self.track.append(Message('program_change', program=12, time=0))

            self.lastTick = glfw.get_time()
            settings.recording = True

    def stopRecording(self):
        if settings.recording:
            settings.recording = False

    def saveRecording(self, name):
        self.file.save("midis/"+name+'.mid')

    def record(self, status, keyIndex, delta):
        if self.file is not None and self.track is not None:
            self.track.append(Message(status, note=64+keyIndex, velocity=64, time=delta))
