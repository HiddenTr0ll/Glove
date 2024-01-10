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
from arm import Arm
from material import Material
import pyrr
from scene import Scene

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
SER_PORT = "COM10"
TARGET_FPS = 60
RETURN_ACTION_CONTINUE = 0
RETURN_ACTION_END = 1


def init():
    global rotationList
    rotationList = [pyrr.matrix44.create_identity() for _ in range(7)]

    global window
    window = initGLFW()

    global texture
    texture = Material("gfx/wood.png")
    glClearColor(0.1, 0.2, 0.4, 1.0)

    global shader
    shader = create_shader_program("shaders/vertex.txt", "shaders/fragment.txt")
    glUseProgram(shader)
    glUniform1i(glGetUniformLocation(shader, "imageTexture"), 0)
    global arm1
    arm1 = Arm()
    glEnable(GL_DEPTH_TEST)

    projectionTransform = pyrr.matrix44.create_perspective_projection(
        fovy=45,
        aspect=SCREEN_WIDTH/SCREEN_HEIGHT,
        near=0.1,
        far=20,
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
    # glfw.swap_interval(1)
    return window


def add():
    # init new arm and add to armlist
    pass


def create_shader_program(vertex_filepath: str, fragment_filepath: str) -> int:
    vertex_module = create_shader_module(vertex_filepath, GL_VERTEX_SHADER)
    fragment_module = create_shader_module(fragment_filepath, GL_FRAGMENT_SHADER)

    shader = compileProgram(vertex_module, fragment_module)

    glDeleteShader(vertex_module)
    glDeleteShader(fragment_module)

    return shader


def create_shader_module(filepath: str, module_type: int) -> int:
    source_code = ""
    with open(filepath, "r") as file:
        source_code = file.readlines()

    return compileShader(source_code, module_type)
