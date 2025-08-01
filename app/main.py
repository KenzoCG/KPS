# ------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------- #

import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
import numpy as np
import ctypes

# ========== SHADERS ==========

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
out vec4 FragColor;

void main()
{
    FragColor = vec4(0.2, 0.6, 1.0, 1.0); // light blue
}
"""

# ========== CUBE DATA ==========

cube_vertices = np.array([
    # positions
    -0.5, -0.5, -0.5,  
     0.5, -0.5, -0.5,  
     0.5,  0.5, -0.5,  
     0.5,  0.5, -0.5,  
    -0.5,  0.5, -0.5,  
    -0.5, -0.5, -0.5,  

    -0.5, -0.5,  0.5,  
     0.5, -0.5,  0.5,  
     0.5,  0.5,  0.5,  
     0.5,  0.5,  0.5,  
    -0.5,  0.5,  0.5,  
    -0.5, -0.5,  0.5,  

    -0.5,  0.5,  0.5,  
    -0.5,  0.5, -0.5,  
    -0.5, -0.5, -0.5,  
    -0.5, -0.5, -0.5,  
    -0.5, -0.5,  0.5,  
    -0.5,  0.5,  0.5,  

     0.5,  0.5,  0.5,  
     0.5,  0.5, -0.5,  
     0.5, -0.5, -0.5,  
     0.5, -0.5, -0.5,  
     0.5, -0.5,  0.5,  
     0.5,  0.5,  0.5,  

    -0.5, -0.5, -0.5,  
     0.5, -0.5, -0.5,  
     0.5, -0.5,  0.5,  
     0.5, -0.5,  0.5,  
    -0.5, -0.5,  0.5,  
    -0.5, -0.5, -0.5,  

    -0.5,  0.5, -0.5,  
     0.5,  0.5, -0.5,  
     0.5,  0.5,  0.5,  
     0.5,  0.5,  0.5,  
    -0.5,  0.5,  0.5,  
    -0.5,  0.5, -0.5
], dtype=np.float32)

# ========== SETUP ==========

def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "3D Cube with OpenGL", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)

    # Compile shaders
    shader = compileProgram(compileShader(VERTEX_SHADER_SRC, GL_VERTEX_SHADER), compileShader(FRAGMENT_SHADER_SRC, GL_FRAGMENT_SHADER))

    # Vertex Array Object & Vertex Buffer Object
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)

    # Vertex positions
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * cube_vertices.itemsize, ctypes.c_void_p(0))

    # Main loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(shader)

        # Model, View, Projection
        model = glm.rotate(glm.mat4(1.0), glfw.get_time() * 5, glm.vec3(0.5, 1.0, 0.0))
        view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
        projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)

        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
