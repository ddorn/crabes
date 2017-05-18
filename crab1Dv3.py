import pygame
from pygame import gfxdraw
from pygame.locals import *
from fractions import Fraction
from time import time

from GUI.buttons import SlideBar
from GUI.draw import *
from GUI.locals import *

pygame.init()
# noinspection PyArgumentList
pygame.key.set_repeat(400, 10)

WHITE = (255, 255, 255)
GREY_25 = (183, 183, 183)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
ORANGE = (255, 127, 20)
PURPLE = (200, 30, 180)

CRABS_COLOR = [BLUE, GREEN, ORANGE, RED, PURPLE]

SCREEN_SIZE = (500, 400)
SETTINGS_SIZE = 150
GRID_SIZE = SCREEN_SIZE[1] // 16


class Crab:
    def __init__(self, i, speed, start):
        self.id = i
        self.start = start
        self.speed = speed
        self.pos_histo = [(0, self.start)]

        self._start = start
        self._speed = speed

    def __str__(self):
        return '(' + str(float(self.start))[:7] + ', ' + str(float(self.speed))[:7] + ')'

    def pos(self, t):
        t = Fraction(t)
        return self.speed * t + self.start  # a*t + b

    def collide(self, x):
        """ Makes a collision at t=x """
        x = Fraction(x)
        y = self.pos(x)

        self.pos_histo.append((x, y))

        self.speed *= -1
        self.start = y - self.speed * x  # New line of movement

    def reset(self):
        self.start = self._start
        self.speed = self._speed
        self.pos_histo = [(0, self.start)]


def draw_grid(surf):
    size = surf.get_size()

    for x in range(GRID_SIZE, size[0], GRID_SIZE):
        gfxdraw.vline(surf, x, 0, size[1], GREY_25)

    for y in range(GRID_SIZE, size[1], GRID_SIZE):
        gfxdraw.hline(surf, 0, size[0], y, GREY_25)

    # axes
    x0, y0 = to_screen_coord(-1, 0)
    x1, y1 = to_screen_coord(size[0] / GRID_SIZE - 1, 0)
    gfxdraw.line(surf, x0, y0, x1, y1, BLACK)
    arrow = [x1, y1,
             x1 - 4, y1 - 4,
             x1 - 4, y1 + 4]
    gfxdraw.filled_trigon(surf, *arrow, BLACK)
    x, _ = to_screen_coord(0, 0)
    gfxdraw.vline(surf, x, 0, size[1], BLACK)


def to_screen_coord(x, y, grid_size=GRID_SIZE):
    # x = 0 when SCREEN_SIZE[0] / 10
    x += 1
    x *= grid_size
    # to have un repère orthonormé
    # minus to have y axe that goes up
    y *= -grid_size
    # y = 0 at SCREEN_SIZE[1] / 2
    y += SCREEN_SIZE[1] / 2

    return int(x), int(y)


def pairs(l):
    for i, elt1 in enumerate(l):
        for j, elt2 in enumerate(l[i + 1:]):
            yield elt1, elt2


def segments(l):
    return zip(l[:-1], l[1:])


def intersection(line1, line2):
    a, b = line1
    m, p = line2

    if m == a:
        return float('inf'), float('inf')

    else:
        x = (p - b) / (a - m)
        y = m * x + p
        return x, y


def update_all_crabs(crabs, max_time):
    already_calculated_time = max(c.pos_histo[-1][0] for c in crabs)
    time = already_calculated_time
    while time < max_time:

        # find the next intersection
        inter_y = []
        lines = [(c.speed, c.start) for c in crabs]

        x_inter_min = max_time
        for l1, l2 in pairs(lines):
            x, y = intersection(l1, l2)
            if time < x < x_inter_min:
                x_inter_min = x
                inter_y = [y]

            # multiples intersections
            elif x == x_inter_min:
                inter_y.append(y)

        time = x_inter_min  # sufficient precision without the floating digits at the end

        for c in crabs:
            if c.pos(time) in inter_y:
                c.collide(time)


def draw_crabs(surf, crabs, max_time):
    for c in crabs[::-1]:

        color = CRABS_COLOR[c.id % len(CRABS_COLOR)]

        # starting pos
        pos = to_screen_coord(*c.pos_histo[0])
        circle(surf, pos, 4, color)

        max_coli = 0
        for a, b in segments(c.pos_histo):
            real_a = to_screen_coord(*a)
            real_b = to_screen_coord(*b)
            if b[0] < max_time:

                line(surf, real_a, real_b, color)
                circle(surf, real_b, 4, color)
                max_coli += 1
            else:
                break

        # draw what remains
        a = c.pos_histo[max_coli]
        if a[0] != max_time:
            # parity number of collision before the end gives the phase
            slope = c.speed * (-1) ** (len(c.pos_histo) - max_coli + 1)
            b = max_time, a[1] + slope * (max_time - a[0])

            real_a = to_screen_coord(*a)
            real_b = to_screen_coord(*b)
            line(surf, real_a, real_b, color)
            circle(surf, real_b, 4, color)


def get_config(file='config.txt'):
    with open(file, 'r') as f:
        config = f.read()

    config = config.split('\n')
    crabs = []
    nb_of_crabs = int(config[0])  # int(input('number of crabs'))
    for i in range(nb_of_crabs):
        crabs.append(Crab(i, *map(Fraction, config[i + 1].split())))

    return crabs


def get_sub_surfaces(display):
    crabs = display.subsurface((0, 0, SCREEN_SIZE[0] - SETTINGS_SIZE, SCREEN_SIZE[1]))

    return crabs


def run(setup):
    global SCREEN_SIZE
    assert isinstance(setup, Setup)

    pygame.display.set_caption("Crab Simulator")
    screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE)
    crabs_screen = get_sub_surfaces(screen)

    def get_funcs(crab):
        def cmd(value):
            value = Fraction(value)
            print(value)
            setup.wait_and_occupy()

            crab._speed = value

            for c_ in setup.crabs:
                c_.reset()

            # update_all_crabs(values.crabs, values.max_time)

            setup.free()
            setup.must_redraw_display()

        def pos():
            return SCREEN_SIZE[0], crab.id * 40

        return cmd, pos

    speed_setters = []
    for c in setup.crabs:
        cmd, pos = get_funcs(c)
        size = (SETTINGS_SIZE, 30)
        color = CRABS_COLOR[c.id % len(CRABS_COLOR)]
        sb = SlideBar(cmd, pos, size, -5, 5, 0.1, color, interval=100, anchor=TOPRIGHT, inital=c.speed, v_type=Fraction)
        speed_setters.append(sb)

    running = True
    while running:

        setup.wait_and_occupy()

        # read events
        for event in pygame.event.get():

            if event.type == QUIT:
                running = False

            if event.type == VIDEORESIZE:
                w, h = event.size
                w = w // GRID_SIZE * GRID_SIZE  # we want a multiple of GRID_SIZE
                h = h // (2 * GRID_SIZE) * 2 * GRID_SIZE  # we want this to be a multiple = 2*GRID_SIZE
                SCREEN_SIZE = w, h
                screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE)
                crabs_screen = get_sub_surfaces(screen)

                setup.must_redraw_display()

            if event.type == KEYDOWN:
                # quit
                if event.key == K_ESCAPE:
                    running = False

                # save picture
                if event.key == K_s:
                    name = f'Crabes {int(time())}.png'
                    print("Image saved to " + name)
                    pygame.image.save(screen, name)

                if event.key == K_LEFT:
                    if setup.max_time:
                        setup.max_time -= 1
                        setup.must_redraw_display()

                if event.key == K_RIGHT:
                    setup.max_time += 1
                    setup.must_redraw_display()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    if setup.max_time:
                        setup.max_time -= 1
                        setup.must_redraw_display()

                if event.button == 5:
                    setup.max_time += 1
                    setup.must_redraw_display()

                mouse = pygame.mouse.get_pos()
                for bar in speed_setters:
                    if mouse in bar:
                        bar.focus()

            if event.type == MOUSEBUTTONUP:
                for bar in speed_setters:
                    bar.unfocus()

        if setup.redraw_display:
            update_all_crabs(setup.crabs, setup.max_time)

            screen.fill(WHITE)

            # crabs part
            draw_grid(crabs_screen)
            draw_crabs(crabs_screen, setup.crabs, setup.max_time)

            # settings part
            for bar in speed_setters:
                bar.render(screen)

            pygame.display.flip()

            setup.display_drawn()

        setup.free()


class Setup:
    def __init__(self):
        self.crabs = get_config()
        self.values = [c.speed for c in self.crabs]
        self.max_time = 0
        self._modif = False
        self.redraw_display = True
        self.last_frame_time = 0

    def _wait_until_free(self):
        while self._modif:
            pass

    def wait_and_occupy(self):
        self._wait_until_free()
        self._modif = True

    def free(self):
        self._modif = False

    def must_redraw_display(self):
        self.redraw_display = True

    def display_drawn(self):
        self.redraw_display = False

    def fps(self, fps):
        while time() < self.last_frame_time + 1 / fps:
            pass

        self.last_frame_time = time()


if __name__ == '__main__':
    setup = Setup()

    # pygame interface
    run(setup)
