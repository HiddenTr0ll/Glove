import numpy as np
import settings
from settings import *
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from key import *
import time

OCTAVES = 3
KEYWIDTHWHITE = 2.22
KEYHEIGHTWHITE = 2
KEYLENGTHWHITE = 13.5

KEYWIDTHBLACK = 1.1
KEYHEIGHTBLACK = 1
KEYLENGTHBLACK = 8.5

KEYSPACING = 2.36


class Keyboard():
    def __init__(self):
        self.fs = None
        self.sfid = None
        if (settings.audioOn):
            self.initAudio()

        #                         x, y, z
        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.keys: list[Key] = []
        self.lastKeysPressed = set()

        for i in range(OCTAVES):
            position = 0
            for j in range(12):
                if j in [0, 2, 4, 5, 7, 9, 11]:  # whitekeys
                    self.keys.append(Key(self.position+np.array([i*7*KEYSPACING + position * KEYSPACING, 0, 0], dtype=np.float32), "white", KEYWIDTHWHITE, KEYHEIGHTWHITE, KEYLENGTHWHITE))
                    position += 1
                else:
                    self.keys.append(Key(self.position+np.array([i*7*KEYSPACING + position * KEYSPACING - KEYSPACING/2, 0,
                                     (KEYHEIGHTWHITE+KEYHEIGHTBLACK)/2], dtype=np.float32), "black", KEYWIDTHBLACK, KEYHEIGHTBLACK, KEYLENGTHBLACK))

    def initAudio(self):
        if self.fs is None:
            try:
                import fluidsynth  # pip install pyFluidSynth
                self.fs = fluidsynth.Synth(samplerate=44100.0)
                self.fs.start()
                self.sfid = self.fs.sfload("soundfonts/concertPiano.sf2")  # for ex. https://musical-artifacts.com/artifacts/3212
                self.fs.program_select(0, self.sfid, 0, 0)
            except:
                print("install fluidsynth and download soundfont to /soundfonts")
                print("fluidsynth: pip install pyFluidSynth")
                print("soundfont example: https://musical-artifacts.com/artifacts/3212")
                settings.audioOn = False

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

    def updatePressed(self, currentlyPressed):
        # set(new) ^ set(old) XOR?
        toRelease = self.lastKeysPressed - currentlyPressed
        toPress = currentlyPressed - self.lastKeysPressed
        self.lastKeysPressed = currentlyPressed
        settings.recorder.recordKeys(toPress, toRelease)
        keyIndex: int
        for keyIndex in toPress:
            self.keys[keyIndex].press()
            if (settings.audioOn):
                self.fs.noteon(0, keyIndex+46, 30)
        for keyIndex in toRelease:
            self.keys[keyIndex].release()
            if (settings.audioOn):
                self.fs.noteoff(0, keyIndex)

    def destroy(self):
        for key in self.keys:
            key.destroy()
