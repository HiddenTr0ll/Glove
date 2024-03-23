import traceback
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *  # noqa: F403
from OpenGL.GL.shaders import compileProgram, compileShader
import serial
import keyboard
import time
import numpy as np
import struct
import csv
import datetime
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
import threading
from material import Material
from scene import Scene
from recorder import Recorder
import sys
import glob
import serial
from read_glove import gloveLoop

import pyrr
import math

import imgui
from imgui.integrations.glfw import GlfwRenderer

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
MODE = 0
TARGET_FPS = 60
RETURN_ACTION_CONTINUE = 0
RETURN_ACTION_END = 1

FONT_PATH = None  # "path/to/font.ttf"
FONT_SCALING_FACTOR = 0.7


def init():
    global mouseSensitivity
    mouseSensitivity = 1

    global movementSpeedH
    movementSpeedH = 1

    global movementSpeedV
    movementSpeedV = 1

    global armPos
    armPos = np.array([20.4, -53, -1.3], dtype=np.float32)

    global armAngle
    armAngle = math.radians(115.41)

    global camPos
    camPos = np.array([-5.17, 18.53, 41.3], dtype=np.float32)

    global camTheta
    camTheta = 320.984017

    global camPhi
    camPhi = -44.240169

    global customTipRadius
    customTipRadius = False

    global tipRadius
    tipRadius = 0.1

    global testRotation
    testRotation = 0
    global testRotation2
    testRotation2 = 0

    global serialPorts
    serialPorts = serial_ports()

    global serialPort
    if len(serialPorts) > 0:
        serialPort = serialPorts[0]
    else:
        serialPort = None

    global gloveThread
    gloveThread = None

    global gloveConnected
    gloveConnected = False

    global running
    running = True

    global recorder
    recorder = Recorder()

    global audioOn
    audioOn = False

    global framerate
    framerate = 0

    global rotationList
    rotationList = [pyrr.matrix44.create_identity() for _ in range(7)]

    imgui.create_context()

    global window
    window = initGLFW()

    global impl
    impl = GlfwRenderer(window)

    global font
    io = imgui.get_io()
    font = io.fonts.add_font_from_file_ttf(FONT_PATH, 30) if FONT_PATH is not None else None
    io.font_global_scale /= FONT_SCALING_FACTOR
    impl.refresh_font_texture()

    global texture
    texture = Material("gfx/wood.png")

    global whiteT
    whiteT = Material("gfx/white.jpg")

    global blackT
    blackT = Material("gfx/black.jpg")

    global shader
    shader = create_shader_program("shaders/vertex.glsl", "shaders/fragment.glsl")
    glUseProgram(shader)
    glUniform1i(glGetUniformLocation(shader, "imageTexture"), 0)

    glEnable(GL_DEPTH_TEST)

    projectionTransform = pyrr.matrix44.create_perspective_projection(
        fovy=45,
        aspect=SCREEN_WIDTH/SCREEN_HEIGHT,
        near=0.1,
        far=200,
        dtype=np.float32)
    glUniformMatrix4fv(
        glGetUniformLocation(shader, "projection"),
        1, GL_FALSE, projectionTransform
    )

    global modelMatrixLocation
    modelMatrixLocation = glGetUniformLocation(shader, "model")
    global viewMatrixLocation
    viewMatrixLocation = glGetUniformLocation(shader, "view")


def initGLFW():
    glfw.init()
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(
        GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT,
        GLFW_CONSTANTS.GLFW_TRUE
    )
    glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, GL_FALSE)

    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "GloveGL", None, None)
    glfw.make_context_current(window)
    glfw.set_input_mode(
        window,
        GLFW_CONSTANTS.GLFW_CURSOR,
        GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
    )
    glClearColor(0.1, 0.2, 0.4, 1.0)

    return window


def add():
    # init new arm and add to armlist
    pass


def create_shader_program(vertex_filepath: str, fragment_filepath: str) -> int:
    vertex_module = create_shader_module(vertex_filepath, GL_VERTEX_SHADER)
    fragment_module = create_shader_module(fragment_filepath, GL_FRAGMENT_SHADER)

    if sys.platform.startswith('darwin'):
        shader = compileProgram(vertex_module, fragment_module, validate=False)
    else:
        shader = compileProgram(vertex_module, fragment_module)
        glDeleteShader(vertex_module)
        glDeleteShader(fragment_module)

    return shader


def create_shader_module(filepath: str, module_type: int) -> int:
    source_code = ""
    with open(filepath, "r") as file:
        source_code = file.readlines()

    return compileShader(source_code, module_type)


def connectGlove():
    global gloveThread
    global gloveConnected
    if gloveConnected:  # stop thread if already running
        gloveThread.run = False
    gloveThread = threading.Thread(target=gloveLoop, args=(serialPort,))
    print("Connecting to Port: " + serialPort)
    gloveThread.start()
    gloveConnected = True


def disconnectGlove():
    global gloveThread
    global gloveConnected
    if gloveConnected:
        gloveThread.run = False
        print("Disconnected from Port: " + serialPort)
        gloveConnected = False


def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
