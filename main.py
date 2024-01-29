from settings import *
import settings
from gui import GUI


class GloveGL:

    def __init__(self):
        settings.init()
        self.mainScene = Scene()
        self.gui = GUI()
        self.glove_thread = None
        self.menuPressed = False
        self.recordMovementPressed = False
        self.recordKeyPressed = False

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
            self.handleKeys()               # handle key inputs
            self.handleEvents()             # check if events should be triggered by key inputs
            if not self.gui.menuEnabled:
                self.handleMouse()

            glfw.poll_events()

            self.gui.render()

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
                settings.movementSpeedH * self.frameTime / 16.7 * np.cos(np.deg2rad(settings.camTheta+directionModifier)),
                settings.movementSpeedH * self.frameTime / 16.7 * np.sin(np.deg2rad(settings.camTheta+directionModifier)),
                0
            ]
            self.mainScene.moveCamera(dPos)
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_E) == GLFW_CONSTANTS.GLFW_PRESS:
            dPos = [
                0,
                0,
                self.frameTime/16.7 * 0.7 * settings.movementSpeedV
            ]
            self.mainScene.moveCamera(dPos)
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_Q) == GLFW_CONSTANTS.GLFW_PRESS:
            dPos = [
                0,
                0,
                self.frameTime/16.7 * -0.7 * settings.movementSpeedV
            ]
            self.mainScene.moveCamera(dPos)

        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) \
                == GLFW_CONSTANTS.GLFW_PRESS:
            if not self.menuPressed:
                self.gui.menuEnabled = not self.gui.menuEnabled
                self.menuPressed = True
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
            self.menuPressed = False

        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_F5) \
                == GLFW_CONSTANTS.GLFW_PRESS:
            if not self.recordKeyPressed:
                if not settings.recorder.recordingKeys:
                    settings.recorder.startKeyRecording()
                    print("started recording keys")
                else:
                    settings.recorder.stopKeyRecording()
                    self.gui.saveDialog("Key")
                    print("stopped recording keys")
                self.recordKeyPressed = True
        else:
            self.recordKeyPressed = False

        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_F6) \
                == GLFW_CONSTANTS.GLFW_PRESS:
            if not self.recordMovementPressed:
                if not settings.recorder.recordingMovement:
                    settings.recorder.startMovementRecording()
                    print("started recording movement")
                else:
                    settings.recorder.stopMovementRecording()
                    self.gui.saveDialog("Movement")
                    print("stopped recording movement")
                self.recordMovementPressed = True
        else:
            self.recordMovementPressed = False

    def handleEvents(self):
        if settings.audioOn:
            self.mainScene.keyboard.initAudio()

    def handleMouse(self):
        (x, y) = glfw.get_cursor_pos(settings.window)
        rate = self.frameTime/16.7*settings.mouseSensitivity*0.1
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
        settings.disconnectGlove()
        self.mainScene.quit()
        glDeleteProgram(settings.shader)
        settings.texture.destroy()
        glfw.destroy_window(settings.window)
        glfw.terminate()
        # settings.impl.shutdown()


glovegl = GloveGL()
