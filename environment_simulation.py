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

time_delta = 1 / 64.0
particle_radii = 6
last_time = 0.0


boxSize = 16
particle_distance = 2 * particle_radii


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.px = x
        self.py = y
        self.r = particle_radii
        self.inv_mass = 1.0


class Constraint:
    def __init__(self, id1, id2, distance):
        self.id1 = id1
        self.id2 = id2
        self.distance = distance
        self.stiffness = 0.05


particles = [
    Particle(
        2.1 * i * particle_radii - boxSize * particle_radii,
        2.1 * j * particle_radii - boxSize * particle_radii,
    )
    for j in range(boxSize)
    for i in range(boxSize)
]

dist_const = 1.5 * particle_distance
distance_constraints = [
    Constraint(i + j * boxSize, i + j * boxSize + 1, dist_const)
    for j in range(boxSize)
    for i in range(boxSize - 1)
]
distance_constraints += [
    Constraint(i + boxSize * j, i + boxSize * (j + 1), dist_const)
    for i in range(boxSize)
    for j in range(boxSize - 1)
]


def mouse_button_callback(window, button, action, mods):
    # create an outwards force at click position
    explosion_force = 50
    x, y = glfw.get_cursor_pos(window)
    x -= 500
    y = -y + 500
    for particle in particles:
        dx = x - particle.x
        dy = y - particle.y
        dist = sqrt(dx * dx + dy * dy)
        particle.px -= explosion_force * dx / pow(dist, 2)
        particle.py -= explosion_force * dy / pow(dist, 2)

    glColor3f(1.0, 0, 0)
    draw_circle(100, x, y)
    glColor3f(1.0, 1.0, 1.0)


def draw():
    glClear(GL_COLOR_BUFFER_BIT)
    drawParticles()
    draw_constrained()
    glFlush()


def draw_constrained():
    for c in distance_constraints:
        glColor3f(0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex2f(particles[c.id1].x, particles[c.id1].y)
        glVertex2f(particles[c.id2].x, particles[c.id2].y)
        glEnd()


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


def wall_constraint(particle):
    dx = 0
    dy = 0

    if particle.x < -WINDOW_SIZE_X / 2 + particle.r:
        dx = particle.x - particle.r + WINDOW_SIZE_X / 2
    elif particle.x > WINDOW_SIZE_X / 2 - particle.r:
        dx = particle.x + particle.r - WINDOW_SIZE_X / 2

    if particle.y < -WINDOW_SIZE_Y / 2 + particle.r:
        dy = particle.y - particle.r + WINDOW_SIZE_Y / 2

    return (-dx, -dy)


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

    if dist < particle_distance:
        offsetDist = dist - particle_distance
        dx1 = offsetDist * dx / 2
        dx2 = -offsetDist * dx / 2
        dy1 = offsetDist * dy / 2
        dy2 = -offsetDist * dy / 2

    return (dx1, dy1, dx2, dy2)


def distance_constraint(constraint):
    particle1 = particles[constraint.id1]
    particle2 = particles[constraint.id2]
    constraint_distance = constraint.distance
    correction_x1 = 0.0
    correction_y1 = 0.0
    correction_x2 = 0.0
    correction_y2 = 0.0

    dx = particle2.x - particle1.x
    dy = particle2.y - particle1.y
    dist = math.sqrt(pow(dx, 2) + pow(dy, 2))

    if dist > 1.4 * constraint_distance:
        distance_constraints.remove(constraint)

    if dist > constraint_distance:
        dx /= dist
        dy /= dist
        sx = 0
        sy = 0

        if dx != 0:
            sx = dx / abs(dx)
        if dy != 0:
            sy = dy / abs(dy)
        correction_x1 = dx * (dist - constraint_distance) / 2
        correction_y1 = dy * (dist - constraint_distance) / 2
        correction_x2 = -correction_x1
        correction_y2 = -correction_y1

    return (correction_x1, correction_y1, correction_x2, correction_y2)


def pbd_main_loop():
    global particles
    gravity = -50
    for particle in particles:
        # line 5 gravity
        particle.vy += gravity * time_delta
        # damp velocities - line 6
        particle.vx *= 0.99
        particle.vy *= 0.99
        # get initial projected positions - line 7
        particle.px = particle.x + particle.vx * time_delta
        particle.py = particle.y + particle.vy * time_delta

        dx, dy = wall_constraint(particle)
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

    # line 9
    for i in range(1, 5):
        # line 10
        for constraint in distance_constraints:
            stiffness = 1 - (1 - constraint.stiffness) ** (1 / i)
            delta_x1, delta_y1, delta_x2, delta_y2 = distance_constraint(constraint)
            particles[constraint.id1].px += stiffness * delta_x1
            particles[constraint.id1].py += stiffness * delta_y1
            particles[constraint.id2].px += stiffness * delta_x2
            particles[constraint.id2].py += stiffness * delta_y2

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
glfw.set_mouse_button_callback(window, mouse_button_callback)
glViewport(0, 0, 1000, 1000)
glOrtho(-500, 500, -500, 500, -1, 1)
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
