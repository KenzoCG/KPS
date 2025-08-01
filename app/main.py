# ------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------- #

import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
import numpy as np
import ctypes

# ------------------------------------------------------------------------------- #
# SHADERS
# ------------------------------------------------------------------------------- #

VERTEX_SHADER_SRC = """
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

FRAGMENT_SHADER_SRC = """
#version 330 core
uniform vec4 uColor;
out vec4 FragColor;

void main()
{
    FragColor = uColor;
}
"""

# ------------------------------------------------------------------------------- #
# CUBE
# ------------------------------------------------------------------------------- #

cube_vertices = np.array([
    -0.5, -0.5, -0.5,  0.5, -0.5, -0.5,  0.5,  0.5, -0.5,
     0.5,  0.5, -0.5, -0.5,  0.5, -0.5, -0.5, -0.5, -0.5,
    -0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5,
     0.5,  0.5,  0.5, -0.5,  0.5,  0.5, -0.5, -0.5,  0.5,
    -0.5,  0.5,  0.5, -0.5,  0.5, -0.5, -0.5, -0.5, -0.5,
    -0.5, -0.5, -0.5, -0.5, -0.5,  0.5, -0.5,  0.5,  0.5,
     0.5,  0.5,  0.5,  0.5,  0.5, -0.5,  0.5, -0.5, -0.5,
     0.5, -0.5, -0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5,
    -0.5, -0.5, -0.5,  0.5, -0.5, -0.5,  0.5, -0.5,  0.5,
     0.5, -0.5,  0.5, -0.5, -0.5,  0.5, -0.5, -0.5, -0.5,
    -0.5,  0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5,  0.5,
     0.5,  0.5,  0.5, -0.5,  0.5,  0.5, -0.5,  0.5, -0.5
], dtype=np.float32)

# ------------------------------------------------------------------------------- #
# APP
# ------------------------------------------------------------------------------- #

def main():
    if not glfw.init():
        raise Exception("GLFW initialization failed")

    window = glfw.create_window(800, 600, "3D + 2D Overlay", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window creation failed")

    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)

    # Compile shader
    shader = compileProgram(
        compileShader(VERTEX_SHADER_SRC, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER_SRC, GL_FRAGMENT_SHADER)
    )

    # --- Setup 3D Cube VAO ---
    cube_vao = glGenVertexArrays(1)
    cube_vbo = glGenBuffers(1)

    glBindVertexArray(cube_vao)
    glBindBuffer(GL_ARRAY_BUFFER, cube_vbo)
    glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))

    # --- Setup 2D UI VAO ---
    ui_vao = glGenVertexArrays(1)
    ui_vbo = glGenBuffers(1)

    glBindVertexArray(ui_vao)
    glBindBuffer(GL_ARRAY_BUFFER, ui_vbo)
    glBufferData(GL_ARRAY_BUFFER, 0, None, GL_DYNAMIC_DRAW)  # Empty for now

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))

    glBindVertexArray(0)

    # --- Main loop ---
    while not glfw.window_should_close(window):
        glfw.poll_events()
        width, height = glfw.get_framebuffer_size(window)

        glViewport(0, 0, width, height)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader)

        # --- Draw 3D Cube ---
        glEnable(GL_DEPTH_TEST)
        model = glm.rotate(glm.mat4(1.0), glfw.get_time(), glm.vec3(0.5, 1.0, 0.0))
        view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
        projection = glm.perspective(glm.radians(45.0), width / height, 0.1, 100.0)

        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))
        glUniform4f(glGetUniformLocation(shader, "uColor"), 0.2, 0.6, 1.0, 1.0)

        glBindVertexArray(cube_vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        # --- Draw 2D Overlay ---
        glDisable(GL_DEPTH_TEST)

        model = glm.mat4(1.0)
        view = glm.mat4(1.0)
        projection = glm.ortho(0, width, height, 0)  # Top-left origin

        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))
        glUniform4f(glGetUniformLocation(shader, "uColor"), 0.5, 0.5, 0.5, 0.5)

        ui_quad = np.array([
            20, 20, 0,
            400, 20, 0,
            400, 200, 0,
            400, 200, 0,
            20, 200, 0,
            20, 20, 0
        ], dtype=np.float32)

        glBindVertexArray(ui_vao)
        glBindBuffer(GL_ARRAY_BUFFER, ui_vbo)
        glBufferData(GL_ARRAY_BUFFER, ui_quad.nbytes, ui_quad, GL_DYNAMIC_DRAW)

        # State - ON
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Draw
        glDrawArrays(GL_TRIANGLES, 0, 6)

        # State - OFF
        glDisable(GL_BLEND)

        # --- Done ---
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
