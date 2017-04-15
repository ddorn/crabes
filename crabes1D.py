import pygame
from pygame import gfxdraw
from pygame.locals import *
from fractions import Fraction
from time import time

pygame.init()
pygame.key.set_repeat(400, 10)

WHITE = (255, 255, 255)
GREY_25 = (183, 183, 183)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (20, 180, 60)
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
        self.t = 0
        self.pos_histo = [(0, self.start)]

    def __str__(self):
        return ('(' + str(float(self.start))[:7] + ', ' + str(float(self.speed))[:7] + ')')

    def pos(self, t):
        return self.speed * t + self.start

    def collide(self, x):
        y = self.pos(x)
        self.pos_histo.append((x, y))

        self.speed *= -1
        self.start = y - self.speed * x

        # print(self.id, x, y)

def draw_grid(screen):
    for x in range(GRID_SIZE, SCREEN_SIZE[0], GRID_SIZE):
        gfxdraw.vline(screen, x, 0, SCREEN_SIZE[1], GREY_25)

    for y in range(GRID_SIZE, SCREEN_SIZE[1], GRID_SIZE):
        gfxdraw.hline(screen, 0, SCREEN_SIZE[0], y, GREY_25)

    # axes
    x0, y0 = to_screen_coord(-1, 0)
    x1, y1 = to_screen_coord(SCREEN_SIZE[0]/GRID_SIZE - 1, 0)
    gfxdraw.line(screen, x0, y0, x1, y1, BLACK)
    arrow = [(x1, y1),
             (x1 - 4, y1 - 4),
             (x1 - 4, y1 + 4)]
    gfxdraw.filled_polygon(screen, arrow, BLACK)
    x, _ = to_screen_coord(0, 0)
    gfxdraw.vline(screen, x, 0, SCREEN_SIZE[1], BLACK)

def to_screen_coord(x, y):

    # x =0 when SCREEN_SIZE[0] / 10
    x += 1
    x *= GRID_SIZE
    # to have un repère orthonormé
    # minus to have y axe that goes up
    y *= -GRID_SIZE
    # y = 0 at SCREEN_SIZE[1] / 2
    y += SCREEN_SIZE[1] / 2

    return int(x), int(y)


def pairs(l):
    for i, elt1 in enumerate(l):
        for j, elt2 in enumerate(l[i+1:]):
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
        y = m*x + p
        return x, y


def update_all_crabs(crabs, collision):
    colli = 0
    time = 0
    while colli < collision:

        # find the next intersection
        inter_y = []
        lines = [(c.speed, c.start) for c in crabs]

        x_inter_min = 100
        for l1, l2 in pairs(lines):
            x, y = intersection(l1, l2)
            if time < x < x_inter_min:
                x_inter_min = x
                inter_y = [y]

            elif x == x_inter_min:
                inter_y.append(y)

        time = x_inter_min  # sufficient precision without the floating digits at the end
        colli += 1

        for c in crabs:
            if c.pos(time) in inter_y:
                c.collide(time)
                pos_now = c.pos_histo[-1]

                # print(pos_now)

    for c in crabs:
        if c.pos_histo[-1][0] != time:
            c.pos_histo.append((time, c.pos(time)))

    return crabs


def draw_crabs(screen, crabs):
    for i, c in enumerate(crabs[::-1]):

        color = CRABS_COLOR[i % len(CRABS_COLOR)]

        x0, y0 = to_screen_coord(*c.pos_histo[0])
        gfxdraw.filled_circle(screen, x0, y0, 4, color)
        gfxdraw.aacircle(screen, x0, y0, 4, color)

        for A, B in segments(c.pos_histo):
            x0, y0 = to_screen_coord(*A)
            x1, y1 = to_screen_coord(*B)
            gfxdraw.line(screen, x0, y0, x1, y1, color)
            gfxdraw.filled_circle(screen, x1, y1, 4, color)
            gfxdraw.aacircle(screen, x1, y1, 4, color)


def run():
    global SCREEN_SIZE

    with open('config.txt', 'r') as f:
        config = f.read()

    config = config.split('\n')
    crabs = []
    nb_of_crabs = int(config[0])  # int(input('number of crabs'))
    for i in range(nb_of_crabs):
        crabs.append(Crab(i, *map(Fraction, config[i + 1].split())))

    crabs_save = [(c.speed, c.start) for c in crabs]

    screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE)
    pygame.display.set_caption("Crab Simulator")

    collisions = 0
    running = True
    while running:

        # read events
        for event in pygame.event.get():

            if event.type == QUIT:
                running = False

            if event.type == VIDEORESIZE:
                w, h = event.size
                w = w // GRID_SIZE * GRID_SIZE  # we want a multiple of GRID_SIZE
                h = h // (2*GRID_SIZE) * 2 * GRID_SIZE  # we want this to be a multiple = 2*GRID_SIZE
                SCREEN_SIZE = w, h
                pygame.display.set_mode(SCREEN_SIZE, RESIZABLE)

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

                # save picture
                if event.key == K_s:
                    name = 'Crabes (' + ','.join(str(Crab(0, *c)) for c in crabs_save) + ").png"
                    print(name)
                    print("Image saved to " + name)
                    pygame.image.save(screen, name)

                if event.key == K_LEFT:
                    collisions -= 1
                    # print('#'*20, 'max_colli = ', collisions)
                    crabs = [Crab(i, *c) for i, c in enumerate(crabs_save)]
                    crabs = update_all_crabs(crabs, collisions)

                if event.key == K_RIGHT:
                    collisions += 1
                    # print('#'*20, 'max_colli = ', collisions)
                    crabs = [Crab(i, *c) for i, c in enumerate(crabs_save)]
                    crabs = update_all_crabs(crabs, collisions)

        screen.fill(WHITE)
        draw_grid(screen)
        draw_crabs(screen, crabs)

        pygame.display.flip()

if __name__ == '__main__':
    run()

"""
2 1
0 3
-2 -1
"""