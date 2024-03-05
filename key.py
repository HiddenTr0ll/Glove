from cuboid import *


class Key(Cuboid):
    def __init__(self, position, color, l, w, h):
        self.isPressed = False
        self.position = position
        self.color = color
        self.l = l
        self.w = w
        self.h = h
        self.eulers = np.array([90, 0, 180], dtype=np.float32)
        self.rotation = pyrr.matrix44.create_from_eulers(
            eulers=np.radians(self.eulers),
            dtype=np.float32)

        super().__init__()

    def press(self):
        self.isPressed = True

    def release(self):
        self.isPressed = False

    def update(self, rate):

        # TODO: update rotation from settings

        if self.isPressed:
            if self.eulers[0] > 85:
                self.eulers[0] -= 0.5 * rate
                if self.eulers[0] < 85:
                    self.eulers[0] = 85
                self.updateRotation(pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.eulers),
                    dtype=np.float32))

        elif self.eulers[0] < 90:
            self.eulers[0] += 0.5 * rate
            if self.eulers[0] > 90:
                self.eulers[0] = 90
            self.updateRotation(pyrr.matrix44.create_from_eulers(
                eulers=np.radians(self.eulers),
                dtype=np.float32))
