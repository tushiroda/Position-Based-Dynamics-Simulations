if __name__ == "__build__":
    raise Exception

import sys
import math
import random
from math import cos as cos
from math import sin as sin
from math import pi as PI
from math import sqrt as sqrt
import glfw

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except BaseException:
    print("""ERROR: PyOpenGL not installed properly.""")
    sys.exit()


WINDOW_SIZE_X = 1000
WINDOW_SIZE_Y = 1000

time_delta = 1 / 128.0
last_time = 0.0
particle_radii = 20
particle_distance = 2 * particle_radii
numParticles = 200
mousex = 0
mousey = 0


class Particle:
    def __init__(self, x, y, goalx):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.px = x
        self.py = y
        self.r = particle_radii
        self.goalx = goalx
        self.goaly = y


class Constraint:
    def __init__(self, id1, id2, distance):
        self.id1 = id1
        self.id2 = id2
        self.distance = distance
        self.stiffness = 0.05


userParticle = Particle(
    random.randint(-WINDOW_SIZE_X / 2, WINDOW_SIZE_X / 2),
    random.randint(-WINDOW_SIZE_Y / 2, WINDOW_SIZE_Y / 2),
    0,
)

particles = [
    Particle(
        random.randint(-WINDOW_SIZE_X / 2, WINDOW_SIZE_X / 2),
        random.randint(-WINDOW_SIZE_Y / 2, WINDOW_SIZE_Y / 2),
        10000,
    )
    for i in range(numParticles)
]
particles += [userParticle]


def draw():
    glClear(GL_COLOR_BUFFER_BIT)
    drawParticles()
    glFlush()


def draw_circle(r, x, y):
    i = 0.0
    glLineWidth(1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    while i <= 360.0:
        glVertex2f(r * cos(PI * i / 180.0) + x, r * sin(PI * i / 180.0) + y)
        i += 360.0 / 18.0
    glEnd()


def drawParticles():
    global particles
    glColor3f(1.0, 1.0, 1.0)
    for particle in particles:
        draw_circle(particle_radii, particle.x, particle.y)
    glColor3f(0, 0, 1.0)
    draw_circle(particle_radii, userParticle.x, userParticle.y)


def check_collision(particle1, particle2):
    dx1 = 0
    dy1 = 0
    dx2 = 0
    dy2 = 0
    dx = particle2.x - particle1.x
    dy = particle2.y - particle1.y
    dist = sqrt(dx * dx + dy * dy)
    if dist != 0:
        dx /= dist
        dy /= dist

    if dist < particle_distance + 3:
        offsetDist = dist - particle_distance - 3
        dx1 = offsetDist * dx / 2
        dx2 = -offsetDist * dx / 2
        dy1 = offsetDist * dy / 2
        dy2 = -offsetDist * dy / 2

    return (dx1, dy1, dx2, dy2)


def wall_constraint(particle):
    dx = 0
    dy = 0

    if particle.x < -WINDOW_SIZE_X / 2 + particle.r:
        particle.x = particle.px = WINDOW_SIZE_X / 2 - particle.r

    elif particle.x > WINDOW_SIZE_X / 2 - particle.r:
        particle.x = particle.px = -WINDOW_SIZE_X / 2 + particle.r

    if particle.y < -WINDOW_SIZE_Y / 2 + particle.r:
        dy = particle.y - particle.r + WINDOW_SIZE_Y / 2
    elif particle.y > WINDOW_SIZE_Y / 2 - particle.r:
        dy = particle.y + particle.r - WINDOW_SIZE_Y / 2

    return (-dx, -dy)


def cursor_position_callback(window, x, y):
    global mousex, mousey
    mousex = x - 500
    mousey = 500 - y


def particle_to_goal(particle):
    weight = 0.4
    dx = particle.goalx - particle.x
    dy = particle.goaly - particle.y

    dist = sqrt(dx * dx + dy * dy)
    dx /= dist
    dy /= dist
    
    if (particle == userParticle):
        weight = 1

    return dx * weight, dy * weight


def pbd_main_loop():
    global particles
    userParticle.goalx = mousex
    userParticle.goaly = mousey
    for particle in particles:
        # damp velocities - line 6
        particle.vx *= 0.9
        particle.vy *= 0.9
        # get initial projected positions - line 7
        particle.px = particle.x + particle.vx * time_delta
        particle.py = particle.y + particle.vy * time_delta

        dx, dy = wall_constraint(particle)
        particle.px += dx
        particle.py += dy

        particle.goaly += random.uniform(-10, 10)

        dx, dy = particle_to_goal(particle)
        particle.px += dx
        particle.py += dy

    # Poll for and process events
    glfw.poll_events()

    # line 8
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            dx1, dy1, dx2, dy2 = check_collision(particles[i], particles[j])
            particles[i].px += dx1
            particles[i].py += dy1
            particles[j].px += dx2
            particles[j].py += dy2

    # line 12
    for particle in particles:
        # line 13
        particle.vx = (particle.px - particle.x) / time_delta
        particle.vy = (particle.py - particle.y) / time_delta
        # line 14
        particle.x = particle.px
        particle.y = particle.py


# Initialize the library
if not glfw.init():
    exit()

# Create a windowed mode window and its OpenGL context
window = glfw.create_window(WINDOW_SIZE_X, WINDOW_SIZE_Y, "Explosions", None, None)
if not window:
    glfw.terminate()
    exit()

# Make the window's context current
glfw.make_context_current(window)

# Set callbacks
# glfw.set_mouse_button_callback(window, mouse_button_callback)
glfw.set_cursor_pos_callback(window, cursor_position_callback)

glViewport(0, 0, 1000, 1000)
glOrtho(
    -WINDOW_SIZE_X / 2, WINDOW_SIZE_X / 2, -WINDOW_SIZE_Y / 2, WINDOW_SIZE_Y / 2, -1, 1
)
# gluOrtho2D(-WINDOW_SIZE_X / 2, WINDOW_SIZE_X / 2, -WINDOW_SIZE_Y / 2, WINDOW_SIZE_Y / 2)

# Main loop
while not glfw.window_should_close(window):
    # Clear the screen with black color
    pbd_main_loop()
    draw()
    # Swap front and back buffers
    glfw.swap_buffers(window)

# Terminate GLFW
glfw.terminate()
