
from OpenGL.GL import *
import glm
import os


def directory_location():
    return os.path.dirname(os.path.abspath(__file__))


def get_shader_source(file_name: str, extension="glsl"):
    current_dir = directory_location()
    file_name = f"{file_name}.{extension}"
    file_path = os.path.join(current_dir, file_name)
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


class Shader:
    def __init__(self):
        self.id = None
        self.vertex_shader = None
        self.fragment_shader = None


    def setup(self, vert_file_name: str, frag_file_name: str):
        # Shader Source
        vert_src = get_shader_source(vert_file_name)
        frag_src = get_shader_source(frag_file_name)

        # Compile shaders
        self.vertex_shader = self.compile_shader(vert_src, GL_VERTEX_SHADER)
        self.fragment_shader = self.compile_shader(frag_src, GL_FRAGMENT_SHADER)

        # Link program
        self.id = glCreateProgram()
        glAttachShader(self.id, self.vertex_shader)
        glAttachShader(self.id, self.fragment_shader)
        glLinkProgram(self.id)

        # Check link status
        success = glGetProgramiv(self.id, GL_LINK_STATUS)
        if not success:
            info_log = glGetProgramInfoLog(self.id)
            raise RuntimeError(f"Shader linking failed:\n{info_log.decode()}")

        # Cleanup shaders (already linked)
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)


    def compile_shader(self, source: str, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        # Check compile status
        success = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not success:
            info_log = glGetShaderInfoLog(shader)
            shader_type_str = "Vertex" if shader_type == GL_VERTEX_SHADER else "Fragment"
            raise RuntimeError(f"{shader_type_str} shader compilation failed:\n{info_log.decode()}")
        return shader


    def is_valid(self):
        return self.id is not None


    def use(self):
        if self.id is not None:
            glUseProgram(self.id)
            return True
        return False


    def set_uniform_int(self, name: str, value: int):
        if self.id is not None and name:
            loc = glGetUniformLocation(self.id, name)
            glUniform1i(loc, value)
            return True
        return False


    def set_uniform_float(self, name: str, value: float):
        if self.id is not None and name:
            loc = glGetUniformLocation(self.id, name)
            glUniform1f(loc, value)
            return True
        return False


    def set_uniform_vec3(self, name: str, vec: glm.vec3):
        if self.id is not None and name:
            loc = glGetUniformLocation(self.id, name)
            glUniform3f(loc, vec.x, vec.y, vec.z)
            return True
        return False


    def set_uniform_vec4(self, name: str, vec: glm.vec4):
        if self.id is not None and name:
            loc = glGetUniformLocation(self.id, name)
            glUniform4f(loc, vec.x, vec.y, vec.z, vec.w)
            return True
        return False


    def set_uniform_mat4(self, name: str, mat: glm.mat4):
        if self.id is not None and name:
            loc = glGetUniformLocation(self.id, name)
            if loc > -1:
                glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(mat))
                return True
        return False


    def delete(self):
        if self.id is not None:
            glDeleteProgram(self.id)
        self.id = None

