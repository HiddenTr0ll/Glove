import numpy as np
import settings
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from limb import *
import pyrr
import math


class Finger():
    def __init__(self, l, w, h, fingerIndex):
        self.fingerIndex = fingerIndex
        #           base   middle   tip
        ratios = (0.4285, 0.2894, 0.2821,  # thumb
                  0.4123, 0.3097, 0.2780,  # index
                  0.4057, 0.3311, 0.2632,  # middle
                  0.3814, 0.3361, 0.2825,  # ring
                  0.3409, 0.3199, 0.3392)  # pinky
        # Ratios modeled after Buryanov & Kotiuk (2010)
        # https://scielo.conicyt.cl/pdf/ijmorphol/v28n3/art15.pdf
        self.phalanges = [Limb(
            l=l,
            w=w,
            h=h * ratios[fingerIndex*3+i]
        ) for i in range(3)]
        self.tipPosition = self.phalanges[2].calculateTip()

    def updateRotation(self, rotationTip, rotationPalm):
        self.phalanges[2].rotation = rotationTip
        self.calculateSubRotations2(rotationTip, rotationPalm)

    def calculateSubRotations(self, rotationTip, rotationPalm):
        tipQuat = pyrr.Quaternion.from_matrix(rotationTip)
        palmQuat = pyrr.Quaternion.from_matrix(rotationPalm)
        identityQuat = pyrr.Quaternion(pyrr.Matrix44.identity())
        dist = palmQuat.inverse * tipQuat  # rotation of tip without rotation of palm

        finger1 = palmQuat * identityQuat.slerp(dist, 0.333)
        finger2 = palmQuat * identityQuat.slerp(dist, 0.666)

        self.phalanges[0].rotation = pyrr.matrix44.create_from_quaternion(finger1)
        self.phalanges[1].rotation = pyrr.matrix44.create_from_quaternion(finger2)

    def calculateSubRotations2(self, rotationTip, rotationPalm):
        tipQuat = pyrr.Quaternion.from_matrix(rotationTip)
        palmQuat = pyrr.Quaternion.from_matrix(rotationPalm)
        identityQuat = pyrr.Quaternion(pyrr.Matrix44.identity())

        dist = tipQuat*palmQuat.inverse   # rotation of tip without rotation of palm

        swing, twist = self.seperateSwingTwist(dist)

        if (swing.w < 0):
            swing = - swing

        x = swing.x

        if self.fingerIndex != 0:  # normal fingers
            if (x < 0) and (swing.w < 0.85):
                x = 2 + x  # 1 loops back to -1 -> -0.95 treated as 1.05

            # Base joint
            # Calculated from
            # -0.0978 -6.4
            #  0       0
            #  0.4254  16.5
            #  0.6992  26.7
            #  0.9377  36.9
            #  1       42
            #  1.0746  54.7

            # Middle joint
            # Calculated from
            # -0.0978 -6.4
            #  0       0
            #  0.4254  31.8
            #  0.6992  64.9
            #  0.9377  103
            #  1       128.5
            #  1.0746  174.9

            if x < -0.0978:
                rotationFactor0 = -6.4
                rotationFactor1 = -6.4
            elif x > 1.0746:
                rotationFactor0 = 54.7
                rotationFactor1 = 174.9
            else:
                rotationFactor0 = 333.3632*(x**5) - 709.3019*(x**4) + 502.5615*(x**3) - 131.4539*(x**2) + 47.3223*x + 0.0152
                rotationFactor1 = 1088.3399*(x**5) - 2175.6519*(x**4) + 1348.4485*(x**3) - 167.0168*(x**2) + 33.7798*x - 0.0186

        else:  # Thumb
            # First joint more range of motion
            # Calculated from
            # -0.5255 -52.2
            # -0.3467 -44.5
            #  0.1033 -19.1
            #  0.5165 - 3.8
            #  0.7985   1.3
            #  0.8882   6.4

            # Middle joint
            # Calculated from
            # -0.5255 -44.5
            # -0.3467 -30.0
            #  0.1033 -11.4
            #  0.5165  26.7
            #  0.7985  54.7
            #  0.8882  70.0

            if x < -0.5255:
                rotationFactor0 = -52.2
                rotationFactor1 = -44.5
            elif x > 0.8882:
                rotationFactor0 = 6.4
                rotationFactor1 = 70.0
            else:
                rotationFactor0 = 78.1614*(x**5) - 14.0924*(x**4) - 74.386*(x**3) - 5.8935*(x**2) + 60.7599*x - 25.2309
                rotationFactor1 = 242.2745*(x**5) - 253.0118*(x**4) - 35.9509*(x**3) + 106.6655*(x**2) + 59.9504*x - 18.6655

        finger0 = pyrr.Quaternion.from_x_rotation(np.deg2rad(rotationFactor0)) * twist * palmQuat
        finger1 = pyrr.Quaternion.from_x_rotation(np.deg2rad(rotationFactor1)) * twist * palmQuat

        self.phalanges[0].rotation = pyrr.matrix44.create_from_quaternion(finger0)
        self.phalanges[1].rotation = pyrr.matrix44.create_from_quaternion(finger1)

    def seperateSwingTwist(self, toSeperate: pyrr.Quaternion):
        swing = pyrr.Quaternion(np.array([toSeperate.x, 0, 0, toSeperate.w]))
        swing = swing.normalised
        twist = swing.inverse * toSeperate

        return swing, twist

    def updatePosition(self, palmTip, palmRotation, offsetX, offsetZ):
        # calculate fingerBot position
        delta = np.dot(np.array([offsetX, 0, offsetZ], dtype=np.float32), palmRotation[:3, :3])
        self.phalanges[0].position = palmTip + delta
        self.phalanges[0].calculateTip()
        self.phalanges[1].position = self.phalanges[0].tipPosition
        self.phalanges[1].calculateTip()
        self.phalanges[2].position = self.phalanges[1].tipPosition
        self.phalanges[2].calculateFingerTip()
        # calculate absolute tip with offset from origin and rotation
        x = self.phalanges[2].tipPosition[0]
        y = self.phalanges[2].tipPosition[1]
        z = self.phalanges[2].tipPosition[2]
        cos = math.cos(settings.armAngle)
        sin = math.sin(settings.armAngle)
        delta_x = x * cos + y * sin
        delta_y = -x * sin + y * cos
        self.tipPosition = np.array([delta_x, delta_y, z]) + settings.armPos

    def overlapsWith(self, cubeList: list[Cuboid]):
        overlapping = []

        for index, cube in enumerate(cubeList):
            # x
            if (self.tipPosition[0]+self.phalanges[2].l/2) < (cube.position[0]-cube.l/2):
                continue

            if (self.tipPosition[0]-self.phalanges[2].l/2) > (cube.position[0]+cube.l/2):
                continue

            # y
            if (self.tipPosition[1]) < (cube.position[1]-cube.h):
                continue

            if (self.tipPosition[1]-2) > (cube.position[1]):
                continue

            # z
            if (self.tipPosition[2]-self.phalanges[2].w/2) > (cube.position[2]+cube.w/2):
                continue

            if (self.tipPosition[2]+self.phalanges[2].w/2) < (cube.position[2]+cube.w/2):
                continue

            overlapping.append(index)
        return overlapping

    def overlapsWithSphere(self, cubeList: list[Cuboid]):
        overlapping = []

        for index, cube in enumerate(cubeList):
            # get box closest point to sphere center by clamping
            #         boxMin       tip      boxMax
            x = max(cube.position[0]-cube.l/2, min(self.tipPosition[0], cube.position[0]+cube.l/2))
            y = max(cube.position[1]-cube.h, min(self.tipPosition[1], cube.position[1]))
            z = max(cube.position[2]-cube.w/2, min(self.tipPosition[2], cube.position[2]+cube.w/2))

            # this is the same as isPointInsideSphere
            distance = math.sqrt(
                (x - self.tipPosition[0]) ** 2 +
                (y - self.tipPosition[1]) ** 2 +
                (z - self.tipPosition[2]) ** 2,
            )
            if settings.customTipRadius:
                radius = settings.tipRadius
            else:
                radius = (self.phalanges[2].w + self.phalanges[2].l)/4
            if distance < radius:
                overlapping.append(index)
        return overlapping

    def draw(self):
        settings.texture.use()
        for phalanx in self.phalanges:
            phalanx.draw()

    def destroy(self):
        for phalanx in self.phalanges:
            phalanx.destroy()
