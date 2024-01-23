from settings import *
import settings
from read_glove import gloveLoop
from gui import GUI


class GloveGL:

    def __init__(self):

        # self.glove_thread = threading.Thread(target=gloveLoop)
        # self.glove_thread.start()

        settings.init()
        self.mainScene = Scene()
        self.gui = GUI()

        self.menuDebounce = 0

        self.lastTime = glfw.get_time()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0

        self.moveLookup = {
            1: 0,
            2: 90,
            3: 45,
            4: 180,
            6: 135,
            7: 90,
            8: 270,
            9: 315,
            11: 0,
            12: 225,
            13: 270,
            14: 180
        }

        self.run()
        self.quit()

    def run(self):
        while not glfw.window_should_close(settings.window) and settings.running:
            if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) \
                    == GLFW_CONSTANTS.GLFW_PRESS:
                if self.menuDebounce == 0:
                    self.gui.menuEnabled = not self.gui.menuEnabled
                    self.menuDebounce = 1000
                    if not self.gui.menuEnabled:
                        glfw.set_input_mode(
                            settings.window,
                            GLFW_CONSTANTS.GLFW_CURSOR,
                            GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
                        )
                        glfw.set_cursor_pos(settings.window, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                    else:
                        glfw.set_input_mode(
                            settings.window,
                            GLFW_CONSTANTS.GLFW_CURSOR,
                            GLFW_CONSTANTS.GLFW_CURSOR_NORMAL
                        )
            else:
                self.menuDebounce = 0

            self.handleKeys()
            if not self.gui.menuEnabled:
                self.handleMouse()
            glfw.poll_events()

            self.gui.render()

            if settings.startRecording:
                settings.startRecording = False
                settings.recording = True
                self.mainScene.keyboard.startRecording()

            if settings.stopRecording:
                settings.stopRecording = False
                settings.recording = False
                self.mainScene.keyboard.stopRecording()

            if settings.save:
                # self.mainScene.keyboard.saveRecording(settings.fileName)
                print(settings.fileName)
                settings.fileName = "NewMidi"
                settings.save = False

            # 1 frame every 16.7ms -> 60fps
            self.mainScene.update(self.frameTime/16.7)
            self.mainScene.render()

            settings.impl.render(imgui.get_draw_data())

            self.calculateFramerate()
            glFlush()

    def handleKeys(self):
        combo = 0
        directionModifier = 0
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 1
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 2
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 4
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 8

        if combo in self.moveLookup:
            directionModifier = self.moveLookup[combo]
            dPos = [
                self.frameTime / 16.7 * np.cos(np.deg2rad(self.mainScene.camTheta+directionModifier)),
                self.frameTime / 16.7 * np.sin(np.deg2rad(self.mainScene.camTheta+directionModifier)),
                0
            ]
            self.mainScene.moveCamera(dPos)
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_E) == GLFW_CONSTANTS.GLFW_PRESS:
            dPos = [
                0,
                0,
                self.frameTime/16.7 * 0.7
            ]
            self.mainScene.moveCamera(dPos)
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_Q) == GLFW_CONSTANTS.GLFW_PRESS:
            dPos = [
                0,
                0,
                self.frameTime/16.7 * -0.7
            ]
            self.mainScene.moveCamera(dPos)

    def handleMouse(self):
        (x, y) = glfw.get_cursor_pos(settings.window)
        rate = self.frameTime/16.7
        thetaInc = rate * ((SCREEN_WIDTH/2)-x)
        phyInc = rate * ((SCREEN_HEIGHT/2)-y)
        self.mainScene.spinCamera(thetaInc, phyInc)
        glfw.set_cursor_pos(settings.window, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

    def calculateFramerate(self):
        self.currentTime = glfw.get_time()
        delta = self.currentTime-self.lastTime
        if (delta >= 1):
            settings.framerate = max(1, int(self.numFrames/delta))
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0/max(1, settings.framerate))
        self.numFrames += 1

    def quit(self):
        # self.glove_thread.run = False
        self.mainScene.quit()
        glDeleteProgram(settings.shader)
        settings.texture.destroy()
        glfw.destroy_window(settings.window)
        glfw.terminate()
        # settings.impl.shutdown()


glovegl = GloveGL()
