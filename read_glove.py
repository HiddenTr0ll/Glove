# -*- coding: utf-8 -*-
"""
Created on Thu May 28 04:15:18 2020

@authors: Jochen, Kristof
"""
import settings
from settings import *
import traceback
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
import serial
import keyboard
import time
import numpy as np
import struct
import csv
import datetime
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R


showData = 1
dataCount = 1000000
maxNumModes = 2

singleNode_Id = 0
glove_v1_Id = 1
glove_v2_Id = 2


hand = {
    "lowerArm": 0,
    "thumb": 1,
    "index": 2,
    "middle": 3,
    "ring": 4,
    "pinky": 5,
    "palm": 6
}


path = "./"


class Joint:
    name = ""
    posX = 0
    posY = 0
    posZ = 0
    rotation = R.from_euler("xyz", [0, 0, 0], degrees=True)


# helper functions for quaternion viz:
def rotate_vector(vector, rotation_matrix):
    return np.dot(rotation_matrix, vector)


def calculate_endpoint(start, a, b, c, d):
    rotation_matrix = R.from_quat([a, b, c, d]).as_matrix()
    unit_vector = np.array([0, 0, 1])
    endpoint = rotate_vector(unit_vector, rotation_matrix)
    return start + endpoint


start_point = np.array([0, 0, 0])


# returns packet data length in bytes (without header bytes)
def getPacketLength(mode, deviceId, packetId):
    if mode == 0:
        if deviceId == singleNode_Id:
            return 8, 1

        elif deviceId == glove_v1_Id:
            return 18, 3

        elif deviceId == glove_v2_Id:
            if packetId == 1:
                return 24, 4
            elif packetId == 2:
                return 18, 3

    elif mode == 1:
        if deviceId == singleNode_Id:
            return 14, 1

        elif deviceId == glove_v1_Id:
            return 24, 2

        elif deviceId == glove_v2_Id:
            if packetId == 1:
                return 24, 2
            elif packetId == 2:
                return 30, 3
            elif packetId == 3:
                return 30, 3

    # if nothing above, input was invalid -> return -1
    return -1


def isPacketValid(mode, deviceId, packetId):
    # for now, only mode = 0 or 1 is allowed. Change this accordingly
    if mode > 1:
        return False
    if packetId == 0 or packetId > 3:
        return False
    if deviceId == 0 and packetId > 1:
        return False
    if mode == 1 and packetId > 2:
        return False
    return True


def gloveLoop(port):
    thisThread = threading.currentThread()

    rotM = np.eye(4)

    #################################
    # open serial port and log file
    #################################
    ser = serial.Serial()
    ser.baudrate = 500000
    ser.port = port
    ser.timeout = 0  # = None means wait forever, = 0 means do not wait
    ser.open()
    # iteration variables for storing to a log file:
    count = 0
    nextTs = 1000
    # helper variables:
    syncBytes = b"\xAB\xCD"
    # syncBytes = b'\x80\x80'
    doSync = False
    # object to store all data
    data = np.zeros((dataCount, 9))

    try:
        ser.reset_input_buffer()

        inData = b""
        mode = -1

        glove_v2_sample_5_pos = -1

        print("start synchronizing")

        # initial synchronization step. Done before starting the timer to not mess up time stamps
        while ser.is_open:
            inData += ser.read(100)
            syncPos = inData.find(syncBytes)
            if syncPos >= 0:
                inData = inData[syncPos + 2:]
                break

        # start timer
        t = time.perf_counter()

        print("start receive loop")
        # receive loop
        while ser.is_open and getattr(thisThread, "run", True):
            # if requested: do synchronization
            if doSync:
                while ser.is_open:
                    inData += ser.read(100)
                    syncPos = inData.find(syncBytes)
                    if syncPos >= 0:
                        inData = inData[syncPos + 2:]
                        doSync = False
                        break

            # time stamp
            ts = int((time.perf_counter() - t) * 1000)

            inData += ser.read(100)
            if len(inData) < 4:
                continue

            # read header (might be sync bytes)
            header = inData[:2]
            if header == syncBytes:
                header = inData[2:4]
                inData = inData[4:]
                # header always has packetId = 1 after sync
                if header[1] & 0x03 != 1:
                    print("got invalid sync sequence. Skip to next sync point")
                    doSync = True
                    continue
            else:
                # strip header data from inData
                inData = inData[2:]

            if header[0] & 0x08 or header[1] & 0x10:
                print(
                    "Received invalid packet header: Control bits invalid. Header is:"
                )
                print(header)
                print("Skip to next sync point...")
                doSync = True
                continue

            # get header data
            nodeId = header[0] >> 4
            deviceId = header[0] & 0x07
            mode = header[1] >> 5
            sampleId = (header[1] >> 2) & 0x03
            packetId = header[1] & 0x03

            # do some basic header check
            if not isPacketValid(mode, deviceId, packetId):
                print(
                    "Received invalid packet header: Mode, deviceId, or packetId invalid."
                )
                print(f"Mode:     {mode}")
                print(f"DeviceID: {deviceId}")
                print(f"PacketId: {packetId}")
                print("Skip to next sync point...")
                doSync = True
                continue

            # Todo: do some more sanity check with header data
            # i.e. check sampleID and packetID not equal to the one before etc.

            packetLength, numSamples = getPacketLength(mode, deviceId, packetId)

            # ensure we already received the whole packet, otherwise wait until it arrives
            while len(inData) < packetLength:
                inData += ser.read(100)

            packet = inData[:packetLength]
            inData = inData[packetLength:]

            if mode == 0:
                if deviceId == singleNode_Id:
                    # packetLength = 8, 1
                    quat = np.array(struct.unpack("<4h", packet)) / 16384
                    settings.recorder.recordMovement([nodeId << 4, ts, quat[1], -quat[3], quat[2], quat[0], 0, 0, 0])

                else:
                    # packetLength = 18, 3 or 24, 4
                    for i in range(numSamples):
                        quatV = (np.array(
                            struct.unpack("<3h", packet[6 * i:6 * (i + 1)])) / 16384)
                        # TODO: Below can result in NaN (Runtimewarning sqrt), dirty fix:
                        sumsq = np.sum(quatV * quatV)
                        if sumsq <= 1:
                            quatW = np.array([np.sqrt(1.0 - sumsq)])
                        else:
                            quatW = np.array([0])

                        if deviceId == glove_v2_Id:
                            ID = (nodeId << 4) + 4 * (packetId - 1) + i
                        else:

                            ID = (nodeId << 4) + numSamples * (packetId - 1) + i

                        # rotating to match real world orientation
                        if ID == 6:  # palm
                            imuQ = R.from_quat([quatV[0], -quatV[2], quatV[1], -quatW[0]])
                            imuQ = imuQ * R.from_euler("xyz", [90, -90, 0], degrees=True)

                        elif ID == 0:  # lower arm
                            imuQ = R.from_quat([quatV[0], quatV[2], -quatV[1], -quatW[0]])

                            imuQ = imuQ * R.from_euler("xyz", [-90, 90, 0], degrees=True)
                        else:
                            imuQ = R.from_quat([quatV[1], -quatV[2], quatV[0], quatW[0]])
                            imuQ = imuQ * R.from_euler("xyz", [-90, 180, 0], degrees=True)

                        #######################################################################################
                        settings.recorder.recordMovement([ID, ts, *imuQ.as_quat(), 0, 0, 0])
                        rotM = np.eye(4)

                        # convert to rotation matrix
                        rotM[:3, :3] = imuQ.as_matrix()
                        # apply rotation
                        settings.rotationList[ID] = rotM

                        count += 1
                        #######################################################################################

            elif mode == 1:
                if deviceId == singleNode_Id:
                    # packetLength = 14, 1
                    rcvd = np.array(struct.unpack("<7h", packet))
                    quat = rcvd[:4] / 16384
                    acc = rcvd[4:] / 100

                    data[count] = [nodeId << 4, ts, quat[1], -quat[3], quat[2], quat[0], -acc[0], acc[2], -acc[1]]
                    count += 1

                elif deviceId == glove_v1_Id:
                    # packetLength = 24, 2
                    for i in range(numSamples):
                        rcvd = np.array(struct.unpack("<6h", packet[12 * i:12 * (i + 1)]))
                        quatV = rcvd[:3] / 16384
                        quatW = np.array([np.sqrt(1.0 - np.sum(quatV * quatV))])
                        acc = rcvd[3:] / 100

                        ID = (nodeId << 4) + numSamples * (packetId - 1) + i
                        data[count] = [ID, ts, quatV[0], -quatV[2], quatV[1], quatW, -acc[0], acc[2], -acc[1]]
                        count += 1

                elif deviceId == glove_v2_Id:
                    if packetId == 1:
                        # packetLength = 24, 2
                        for i in range(numSamples):
                            rcvd = np.array(struct.unpack("<6h", packet[12 * i:12 * (i + 1)]))
                            quatV = rcvd[:3] / 16384
                            quatW = np.array([np.sqrt(1.0 - np.sum(quatV * quatV))])
                            acc = rcvd[3:] / 100

                            ID = (nodeId << 4) + numSamples * (packetId - 1) + i
                            data[count] = [ID, ts, quatV[0], -quatV[2], quatV[1], quatW, -acc[0], acc[2], -acc[1]]
                            count += 1

                            # here we need to pay attention for packets 2 and 3 because sample #5
                            # is spread across both packets
                            # When we see packet 1, we invalidate it in case packet 2 or 3 went missing
                            glove_v2_sample_5_pos = -1

                    elif packetId == 2:
                        # packetLength = 30, 3
                        for i in range(numSamples):
                            rcvd = np.array(struct.unpack("<6h", packet[12 * i:12 * (i + 1)]))
                            quatV = rcvd[:3] / 16384
                            quatW = np.array([np.sqrt(1.0 - np.sum(quatV * quatV))])
                            acc = rcvd[3:] / 100

                            ID = (nodeId << 4) + numSamples * (packetId - 1) + i
                            data[count] = [ID, ts, quatV[0], -quatV[2], quatV[1], quatW, -acc[0], acc[2], -acc[1]]
                            count += 1

                        quatV = np.array(struct.unpack("<3h", packet[24:30])) / 16384
                        quatW = np.array([np.sqrt(1.0 - np.sum(quatV * quatV))])
                        data[count] = [ID, ts, quatV[0], -quatV[2], quatV[1], quatW, 0, 0, 0]

                        glove_v2_sample_5_pos = count
                        count += 1

                    elif packetId == 3:
                        # packetLength = 30, 3
                        for i in range(numSamples):
                            rcvd = np.array(struct.unpack("<6h", packet[12 * i:12 * (i + 1)]))
                            quatV = rcvd[:3] / 16384
                            quatW = np.array([np.sqrt(1.0 - np.sum(quatV * quatV))])
                            acc = rcvd[3:] / 100

                            ID = (nodeId << 4) + numSamples * (packetId - 1) + i
                            data[count] = [ID, ts, quatV[0], -quatV[2], quatV[1], quatW, -acc[0], acc[2], -acc[1]]
                            count += 1

                        acc = np.array(struct.unpack("<3h", packet[24:30])) / 100

                        if glove_v2_sample_5_pos > 0:
                            data[glove_v2_sample_5_pos][6:9] = [-acc[0], acc[2], -acc[1]]
                            count += 1
                        # else:
                        # packet 2 is missing

            # data[count][0] = nodeId << 4 # create unique ID from nodeId, packetId, and actual IMU sample
            # data[count][1] = ts

            # quat is in format wxyz -> change IMU coordinates to correct format xyzw
            # also in quaternion coordinates z is up, in screen coordinates y is up -> switch axes to (x, -z, y, w)
            # data[count][2] = quat[1] # x
            # data[count][3] = -quat[3] # y
            # data[count][4] = quat[2] # z
            # data[count][5] = quat[0] # w

            # if mode == 1:
            # in screen coordinates y is up -> switch axes to (-x, z, -y)
            # data[count][6] = -acc[0] # x
            # data[count][7] = acc[2] # y
            # data[count][8] = -acc[1] # z

            # count += 1

            if ts >= nextTs:
                # print('time: ' + str(ts/1000) + '  count: ' + str(count))
                nextTs += 1000

    except Exception as e:
        print("An error occured during recording")
        print(e)
        print(traceback.format_exc())

    finally:
        ser.close()
