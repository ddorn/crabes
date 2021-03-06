import pygame
from _thread import start_new_thread
from pygame import gfxdraw
from pygame.locals import *
from fractions import Fraction

from tkinter import *

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


def draw_grid(screen):
    for x in range(GRID_SIZE, SCREEN_SIZE[0], GRID_SIZE):
        gfxdraw.vline(screen, x, 0, SCREEN_SIZE[1], GREY_25)

    for y in range(GRID_SIZE, SCREEN_SIZE[1], GRID_SIZE):
        gfxdraw.hline(screen, 0, SCREEN_SIZE[0], y, GREY_25)

    # axes
    x0, y0 = to_screen_coord(-1, 0)
    x1, y1 = to_screen_coord(SCREEN_SIZE[0] / GRID_SIZE - 1, 0)
    gfxdraw.line(screen, x0, y0, x1, y1, BLACK)
    arrow = [(x1, y1),
             (x1 - 4, y1 - 4),
             (x1 - 4, y1 + 4)]
    gfxdraw.filled_polygon(screen, arrow, BLACK)
    x, _ = to_screen_coord(0, 0)
    gfxdraw.vline(screen, x, 0, SCREEN_SIZE[1], BLACK)


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
        # print('wtf', line1, line2)
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


def draw_crabs(screen, crabs, max_time):
    for i, c in enumerate(crabs[::-1]):

        color = CRABS_COLOR[i % len(CRABS_COLOR)]

        # starting pos
        x0, y0 = to_screen_coord(*c.pos_histo[0])
        gfxdraw.filled_circle(screen, x0, y0, 4, color)
        gfxdraw.aacircle(screen, x0, y0, 4, color)

        max_coli = 0
        for a, b in segments(c.pos_histo):
            x0, y0 = to_screen_coord(*a)
            x1, y1 = to_screen_coord(*b)
            if b[0] < max_time:
                gfxdraw.line(screen, x0, y0, x1, y1, color)
                gfxdraw.filled_circle(screen, x1, y1, 4, color)
                gfxdraw.aacircle(screen, x1, y1, 4, color)
                max_coli += 1
            else:
                break

        # draw what remains
        a = c.pos_histo[max_coli]
        if a[0] != max_time:
            # parity number of collision before the end gives the phase
            slope = c.speed * (-1) ** (len(c.pos_histo) - max_coli + 1)
            b = max_time, a[1] + slope * (max_time - a[0])

            x0, y0 = to_screen_coord(*a)
            x1, y1 = to_screen_coord(*b)
            gfxdraw.line(screen, x0, y0, x1, y1, color)
            gfxdraw.filled_circle(screen, x1, y1, 4, color)
            gfxdraw.aacircle(screen, x1, y1, 4, color)


def get_config(file='config.txt'):
    with open(file, 'r') as f:
        config = f.read()

    config = config.split('\n')
    crabs = []
    nb_of_crabs = int(config[0])  # int(input('number of crabs'))
    for i in range(nb_of_crabs):
        crabs.append(Crab(i, *map(Fraction, config[i + 1].split())))

    return crabs


CRABS = get_config()


def run(values):
    global SCREEN_SIZE
    assert isinstance(values, Values)

    screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE)
    pygame.display.set_caption("Crab Simulator")
    clock = pygame.time.Clock()

    running = True
    while running:

        values.wait_until_free()
        values.occupy()

        # read events
        for event in pygame.event.get():

            if event.type == QUIT:
                running = False

            if event.type == VIDEORESIZE:
                w, h = event.size
                w = w // GRID_SIZE * GRID_SIZE  # we want a multiple of GRID_SIZE
                h = h // (2 * GRID_SIZE) * 2 * GRID_SIZE  # we want this to be a multiple = 2*GRID_SIZE
                SCREEN_SIZE = w, h
                pygame.display.set_mode(SCREEN_SIZE, RESIZABLE)

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

                # save picture
                if event.key == K_s:
                    from time import time
                    name = f'Crabes {int(time())}.png'
                    print("Image saved to " + name)
                    pygame.image.save(screen, name)

                if event.key == K_LEFT:
                    if values.max_time:
                        values.max_time -= 1
                        update_all_crabs(values.crabs, values.max_time)

                if event.key == K_RIGHT:
                    values.max_time += 1
                    update_all_crabs(values.crabs, values.max_time)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    if values.max_time:
                        values.max_time -= 1
                        update_all_crabs(values.crabs, values.max_time)

                if event.button == 5:
                    values.max_time += 1
                    update_all_crabs(values.crabs, values.max_time)

        screen.fill(WHITE)
        draw_grid(screen)
        draw_crabs(screen, values.crabs, values.max_time)

        values.free()
        clock.tick(60)

        pygame.display.flip()


class Values:
    def __init__(self):
        self.crabs = get_config()
        self.values = [c.speed for c in self.crabs]
        self.max_time = 0
        self._modif = False

    def wait_until_free(self):
        while self._modif:
            pass
        
    def occupy(self):
        self._modif = True
        
    def free(self):
        self._modif = False


if __name__ == '__main__':
    values = Values()

    # pygame interface
    # start_new_thread(run, (values,))
    run(values)
    quit()
    # tk inter inteface to choses values
    root = Tk()

    def meta_cd(i):
        def cmd(value):
            values.wait_until_free()
            values.occupy()

            c = values.crabs[i]
            c._speed = Fraction(value)

            for c in values.crabs:
                c.reset()

            update_all_crabs(values.crabs, values.max_time)
            print(i, value)

            values.free()

        return cmd

    for i in range(len(values.crabs)):
    
        s = Scale(root, orient=HORIZONTAL, length=200, from_=-5.0, to=5.0, resolution=0.001, digits=2, command=meta_cd(i))
        s.set(float(values.crabs[i].speed))
        s.pack()


    root.mainloop()

"""
2 1
0 3
-2 -1
"""
