# ------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------- #

import glfw
from OpenGL.GL import *
import glm

# ------------------------------------------------------------------------------- #
# TABLES
# ------------------------------------------------------------------------------- #

KEYS = {
    'ESCAPE' : glfw.KEY_ESCAPE,
    'SPACE'  : glfw.KEY_SPACE,
    'W'      : glfw.KEY_W,
    'A'      : glfw.KEY_A,
    'S'      : glfw.KEY_S,
    'D'      : glfw.KEY_D,
}

# ------------------------------------------------------------------------------- #
# CLASS
# ------------------------------------------------------------------------------- #

class Window:
    def __init__(self, width=800, height=600, title="KenzoCG Python App"):
        # Window
        self.window = None
        self.width = width
        self.height = height
        self.title = title
        # Timing
        self.last_time = 0.0
        self.current_time = 0.0
        self.delta_time = 0.0
        # State
        self.valid = False


    def setup(self):
        # State
        self.valid = False
        # Initialize GLFW
        if not glfw.init():
            raise Exception("GLFW could not be initialized!")
        # Configure OpenGL context
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # Create the window
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            self.valid = False
            glfw.terminate()
            raise Exception("Failed to create GLFW window!")
        # Make the OpenGL context current
        glfw.make_context_current(self.window)
        # Set resize callback
        glfw.set_framebuffer_size_callback(self.window, self.resize_callback)
        self.valid = True


    def resize_callback(self, window, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, self.width, self.height)


    def run(self, update_func, draw_3d_func, draw_2d_func=None):
        # Main Loop
        while not glfw.window_should_close(self.window):
            # Time
            self.current_time = glfw.get_time()
            self.delta_time = self.current_time - self.last_time
            # Clear
            width, height = glfw.get_framebuffer_size(self.window)
            glEnable(GL_DEPTH_TEST)
            glViewport(0, 0, width, height)
            glClearColor(0.1, 0.1, 0.1, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # Event
            glfw.poll_events()
            # Update
            if callable(update_func):
                update_func(self)
            # Draw 3D
            if callable(draw_3d_func):
                draw_3d_func(self)
            # Draw 2D
            if callable(draw_2d_func):
                draw_2d_func(self)
            # Swap
            glfw.swap_buffers(self.window)
            # Time
            self.last_time = self.current_time
        # Terminate
        self.terminate()


    def stop(self):
        if self.window is not None:
            glfw.set_window_should_close(self.window, True)


    def terminate(self):
        self.stop()
        glfw.terminate()
        self.window = None


    def is_key_pressed(self, key: str):
        if self.window is not None:
            value = KEYS.get(key)
            if value is not None:
                return glfw.get_key(self.window, value) == glfw.PRESS
        return False


    def get_cursor_pos(self):
        if self.window is not None:
            x, y = glfw.get_cursor_pos(self.window)
            return glm.vec2(x, y)
        return None
