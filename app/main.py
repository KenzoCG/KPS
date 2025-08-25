# ------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------- #

from OpenGL.GL import *
import glm

from . import utils
from . import shaders

from .components.window import Window

# ------------------------------------------------------------------------------- #
# INIT
# ------------------------------------------------------------------------------- #

SHADER = None

CUBE_VAO = None
CUBE_VBO = None

SQUARE_VAO = None
SQUARE_VBO = None


def setup():

    # --- Shaders --- #
    global SHADER
    SHADER = shaders.Shader()
    SHADER.setup(vert_file_name="vert", frag_file_name="frag")
    if not SHADER.is_valid():
        return False


    # --- 3D --- #
    global CUBE_VAO, CUBE_VBO
    verts = utils.presets.cube_verts()

    CUBE_VAO = glGenVertexArrays(1)
    CUBE_VBO = glGenBuffers(1)

    glBindVertexArray(CUBE_VAO)
    glBindBuffer(GL_ARRAY_BUFFER, CUBE_VBO)
    glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts.ptr, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))


    # --- 2D --- #
    global SQUARE_VAO, SQUARE_VBO
    SQUARE_VAO = glGenVertexArrays(1)
    SQUARE_VBO = glGenBuffers(1)

    glBindVertexArray(SQUARE_VAO)
    glBindBuffer(GL_ARRAY_BUFFER, SQUARE_VBO)
    glBufferData(GL_ARRAY_BUFFER, 0, None, GL_DYNAMIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))

    glBindVertexArray(0)
    return True

# ------------------------------------------------------------------------------- #
# CALLBACKS
# ------------------------------------------------------------------------------- #

def update(window: Window):
    pass


def draw_3d(window: Window):
    # Projections
    model = glm.rotate(glm.mat4(1.0), window.current_time, glm.vec3(0.5, 1.0, 0.0))
    view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
    fov = glm.radians(45.0)
    aspect =  window.width / window.height
    near = 0.1
    far =  100.0
    projection = glm.perspective(fov, aspect, near, far)

    # Shader
    SHADER.use()
    SHADER.set_uniform_mat4(name="model", mat=model)
    SHADER.set_uniform_mat4(name="view", mat=view)
    SHADER.set_uniform_mat4(name="projection", mat=projection)
    SHADER.set_uniform_vec4(name="uColor", vec=glm.vec4(0.2, 0.6, 1.0, 1.0))

    # Arrays
    glBindVertexArray(CUBE_VAO)

    # Draw
    glDrawArrays(GL_TRIANGLES, 0, 36)

    # Depth - OFF
    glDisable(GL_DEPTH_TEST)


def draw_2d(window: Window):
    # Projections
    model = glm.mat4(1.0)
    view = glm.mat4(1.0)
    projection = glm.ortho(0, window.width, window.height, 0)

    # Shader
    SHADER.use()
    SHADER.set_uniform_mat4(name="model", mat=model)
    SHADER.set_uniform_mat4(name="view", mat=view)
    SHADER.set_uniform_mat4(name="projection", mat=projection)
    SHADER.set_uniform_vec4(name="uColor", vec=glm.vec4(0.5, 0.5, 0.5, 0.5))

    # Verts
    verts = utils.presets.square_verts()

    # Arrays
    glBindVertexArray(SQUARE_VAO)
    glBindBuffer(GL_ARRAY_BUFFER, SQUARE_VBO)
    glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts.ptr, GL_DYNAMIC_DRAW)

    # Blend - ON
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Draw
    glDrawArrays(GL_TRIANGLES, 0, 6)

    # Blend - OFF
    glDisable(GL_BLEND)

# ------------------------------------------------------------------------------- #
# APP
# ------------------------------------------------------------------------------- #

def main():
    window = Window(width=800, height=600, title="KenzoCG Python App")
    window.setup()
    if not window.valid:
        window.close()
        return
    if not setup():
        window.close()
        return
    window.run(update_func=update, draw_3d_func=draw_3d, draw_2d_func=draw_2d)


if __name__ == "__main__":
    main()
