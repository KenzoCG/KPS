
'''

IDEA
    - Model each letter and number and then use the model data to create the text for drawing.
    - Ideally loading each letter into a batch and drawing it at the proper location.
    - Would need a way to batch everything.

'''


import json
import ctypes
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

# ---------- Math helpers ----------
def translate(x, y, z=0.0):
    m = np.eye(4, dtype=np.float32)
    m[3, 0] = x
    m[3, 1] = y
    m[3, 2] = z
    return m

def scale(sx, sy, sz=1.0):
    m = np.eye(4, dtype=np.float32)
    m[0, 0] = sx
    m[1, 1] = sy
    m[2, 2] = sz
    return m

def ortho(left, right, bottom, top, near, far):
    m = np.zeros((4,4), dtype=np.float32)
    m[0,0] = 2.0 / (right - left)
    m[1,1] = 2.0 / (top - bottom)
    m[2,2] = -2.0 / (far - near)
    m[3,0] = -(right + left) / (right - left)
    m[3,1] = -(top + bottom) / (top - bottom)
    m[3,2] = -(far + near) / (far - near)
    m[3,3] = 1.0
    return m

# ---------- Shader sources ----------
VERTEX_SRC = """
#version 330 core
layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec3 a_norm;
layout(location = 2) in vec2 a_uv;

// instanced model matrix (4 vec4s)
layout(location = 3) in vec4 i_model_row0;
layout(location = 4) in vec4 i_model_row1;
layout(location = 5) in vec4 i_model_row2;
layout(location = 6) in vec4 i_model_row3;

uniform mat4 u_view;
uniform mat4 u_proj;
uniform vec3 u_color;

out vec3 v_color;

mat4 instance_model() {
    return mat4(i_model_row0, i_model_row1, i_model_row2, i_model_row3);
}

void main() {
    mat4 model = instance_model();
    gl_Position = u_proj * u_view * model * vec4(a_pos, 1.0);
    v_color = u_color;
}
"""

FRAGMENT_SRC = """
#version 330 core
in vec3 v_color;
out vec4 frag_color;
void main() {
    frag_color = vec4(v_color, 1.0);
}
"""

class BatchedTextRenderer:
    def __init__(self, json_path, window_size=(800, 600), default_advance=1.0):
        # compile shader
        self.shader = compileProgram(
            compileShader(VERTEX_SRC, GL_VERTEX_SHADER),
            compileShader(FRAGMENT_SRC, GL_FRAGMENT_SHADER),
        )

        self.default_advance = default_advance
        self.advances = {}
        self.glyph_offsets = {}  # for potential per-glyph usage
        self.instance_count = 0

        # Load and pack glyphs
        with open(json_path, 'r') as f:
            data = json.load(f)

        all_vertices = []
        all_indices = []
        vertex_offset = 0  # in number of vertices (not bytes)
        for ch, obj in data.items():
            verts = obj['vertices']
            inds = obj['indices']
            num_verts = len(verts) // 8  # assuming layout: pos3, norm3, uv2

            # record advance
            self.advances[ch] = obj.get('advance', self.default_advance)
            self.glyph_offsets[ch] = (vertex_offset, len(inds))  # optional

            all_vertices.extend(verts)
            # shift indices by current vertex offset
            shifted = [i + vertex_offset for i in inds]
            all_indices.extend(shifted)
            vertex_offset += num_verts

        # Convert to numpy
        vertex_data = np.array(all_vertices, dtype=np.float32)
        index_data = np.array(all_indices, dtype=np.uint32)
        self.total_index_count = len(index_data)

        # Create VAO/VBO/EBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

        stride = 8 * ctypes.sizeof(ctypes.c_float)  # pos3 + norm3 + uv2 = 8 floats
        # position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        # normal
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        # uv
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * ctypes.sizeof(ctypes.c_float)))

        # Instance buffer for model matrices (we'll allocate max on demand)
        self.instance_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
        # initially empty
        glBufferData(GL_ARRAY_BUFFER, 0, None, GL_DYNAMIC_DRAW)

        # Set up four vec4 attributes for matrix, locations 3,4,5,6
        bytes_per_mat = 16 * ctypes.sizeof(ctypes.c_float)
        for i in range(4):
            loc = 3 + i
            glEnableVertexAttribArray(loc)
            offset = i * 4 * ctypes.sizeof(ctypes.c_float)
            glVertexAttribPointer(loc, 4, GL_FLOAT, GL_FALSE, bytes_per_mat, ctypes.c_void_p(offset))
            glVertexAttribDivisor(loc, 1)  # advance per instance

        glBindVertexArray(0)

        # Setup projection/view (orthographic)
        w, h = window_size
        self.proj = ortho(0, w, 0, h, -1, 1)
        self.view = np.eye(4, dtype=np.float32)

        # Uniform locations
        self.u_view = glGetUniformLocation(self.shader, "u_view")
        self.u_proj = glGetUniformLocation(self.shader, "u_proj")
        self.u_color = glGetUniformLocation(self.shader, "u_color")


    def build_instance_buffer(self, text, position, scale=1.0, align="left"):
        x, y = position
        # alignment adjustment
        if align != "left":
            total_adv = sum(self.advances.get(ch, self.default_advance) for ch in text) * scale
            if align == "center":
                x -= total_adv * 0.5
            elif align == "right":
                x -= total_adv

        mats = []
        cursor = x
        for ch in text:
            advance = self.advances.get(ch, self.default_advance)
            model = np.matmul(translate(cursor, y, 0.0), scale(scale, scale, 1.0))
            mats.append(model.T.reshape(16))  # transpose because GLSL expects column-major
            cursor += advance * scale

        if len(mats) == 0:
            self.instance_count = 0
            return

        mat_array = np.array(mats, dtype=np.float32)  # shape: (N,16)
        self.instance_count = len(mats)

        # upload to instance VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
        glBufferData(GL_ARRAY_BUFFER, mat_array.nbytes, mat_array, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)


    def draw_text(self, text, position, scale=1.0, color=(1.0, 1.0, 1.0), align="left"):
        # prepare instance data
        self.build_instance_buffer(text, position, scale, align)
        if self.instance_count == 0:
            return

        glUseProgram(self.shader)
        # upload camera
        glUniformMatrix4fv(self.u_proj, 1, GL_FALSE, self.proj.flatten())
        glUniformMatrix4fv(self.u_view, 1, GL_FALSE, self.view.flatten())
        glUniform3f(self.u_color, *color)

        glBindVertexArray(self.vao)
        # Single draw call for all characters
        glDrawElementsInstanced(GL_TRIANGLES, self.total_index_count, GL_UNSIGNED_INT, None, self.instance_count)
        glBindVertexArray(0)
        glUseProgram(0)
