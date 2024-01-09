from settings import *
import settings


class GloveGL:

    def __init__(self):

        # glove_thread = threading.Thread(target=gloveLoop)
        # glove_thread.start()

        settings.init()
        self.arm1 = settings.arm1
        self.mainScene = Scene()

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
        while not glfw.window_should_close(settings.window):
            if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) \
                    == GLFW_CONSTANTS.GLFW_PRESS:
                break

            self.handleKeys()
            # self.handleMouse()
            glfw.poll_events()

            # 1 frame every 16.7ms -> 60fps
            # self.mainScene.update(self.frameTime/16.7)
            self.mainScene.render()

            # glFlush()
            # glfw.swap_buffers(settings.window)

            self.calculateFramerate()

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
                0.1*self.frameTime / 16.7 * np.cos(np.deg2rad(self.mainScene.camTheta+directionModifier)),
                0.1*self.frameTime / 16.7 * np.sin(np.deg2rad(self.mainScene.camTheta+directionModifier)),
                0
            ]
            self.mainScene.moveCamera(dPos)
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_E) == GLFW_CONSTANTS.GLFW_PRESS:
            dPos = [
                0,
                0,
                self.frameTime/16.7 * 0.1
            ]
            self.mainScene.moveCamera(dPos)
        if glfw.get_key(settings.window, GLFW_CONSTANTS.GLFW_KEY_Q) == GLFW_CONSTANTS.GLFW_PRESS:
            dPos = [
                0,
                0,
                self.frameTime/16.7 * -0.1
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
            framerate = max(1, int(self.numFrames/delta))
            glfw.set_window_title(settings.window, f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0/max(1, framerate))
        self.numFrames += 1

    def quit(self):
        glDeleteVertexArrays(len(self.arm1.limbs), [o.vao for o in self.arm1.limbs])
        glDeleteProgram(settings.shader)
        settings.texture.destroy()
        glfw.destroy_window(settings.window)
        glfw.terminate()


glovegl = GloveGL()
