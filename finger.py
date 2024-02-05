import numpy as np
import settings
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from limb import *
import pyrr


fingerAdjust1 = pyrr.Quaternion.from_x_rotation(np.deg2rad(0.33333*360))
fingerAdjust2 = pyrr.Quaternion.from_x_rotation(np.deg2rad(0.66666*360))


class Finger():
    def __init__(self, l, w, h, fingerIndex):
        self.fingerIndex = fingerIndex
        #  base   middle   tip
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

        if self.fingerIndex != 0:  # normal fingers
            finger1 = identityQuat.slerp(swing, 0.33333) * twist * palmQuat
            finger2 = identityQuat.slerp(swing, 0.66666) * twist * palmQuat

            # slerp flips at some point because of shortest path calculation
            if swing.x < -0.35:  # -> rotate to take the long path again
                finger1 = fingerAdjust1 * finger1  # fingerAdjust1 = 1/3*360°
                finger2 = fingerAdjust2 * finger2  # fingerAdjust2 = 2/3*360°

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

            x = swing.x

            if x < -0.5255:
                rotationFactor0 = -52.2
                rotationFactor1 = -44.5
            elif x > 0.8882:
                rotationFactor0 = 6.4
                rotationFactor1 = 70.0
            else:
                rotationFactor0 = 78.1614*(x**5) - 14.0924*(x**4) - 74.386*(x**3) - 5.8935*(x**2) + 60.7599*x - 25.2309
                rotationFactor1 = 242.2745*(x**5) - 253.0118*(x**4) - 35.9509*(x**3) + 106.6655*(x**2) + 59.9504*x - 18.6655

            finger1 = pyrr.Quaternion.from_x_rotation(np.deg2rad(rotationFactor0)) * twist * palmQuat
            finger2 = pyrr.Quaternion.from_x_rotation(np.deg2rad(rotationFactor1)) * twist * palmQuat

        self.phalanges[0].rotation = pyrr.matrix44.create_from_quaternion(finger1)
        self.phalanges[1].rotation = pyrr.matrix44.create_from_quaternion(finger2)

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
        self.phalanges[2].calculateTip()
        self.tipPosition = self.phalanges[2].tipPosition

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

    def draw(self):
        settings.texture.use()
        for phalanx in self.phalanges:
            phalanx.draw()
