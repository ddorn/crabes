import collections
import pygame
from _dummy_thread import start_new_thread
from pygame import gfxdraw
from pygame.locals import *

pygame.init()
pygame.key.set_repeat(100)

WHITE = (255, 255, 255)
GREY_25 = (183, 183, 183)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (20, 180, 60)
ORANGE = (200, 140, 20)
PURPLE = (200, 30, 180)

CRABS_COLOR = [BLUE, GREEN, ORANGE, RED, PURPLE]

SCREEN_SIZE = (500, 400)
GRID_SIZE = SCREEN_SIZE[1] // 16


class Crab:
    def __init__(self, speed, start):
        self.start = start
        self.speed = speed
        self.t = 0
        self.pos_histo = [(0, self.start)]

    def pos(self, t):
        return self.speed * t + self.start

    def collide(self, x):
        y = self.pos(x)
        self.pos_histo.append((x, y))

        self.speed *= -1
        self.start = y - self.speed * x


def draw_grid(screen):
    for x in range(GRID_SIZE, SCREEN_SIZE[0], GRID_SIZE):
        gfxdraw.vline(screen, x, 0, SCREEN_SIZE[1], GREY_25)

    for y in range(GRID_SIZE, SCREEN_SIZE[1], GRID_SIZE):
        gfxdraw.hline(screen, 0, SCREEN_SIZE[0], y, GREY_25)


def to_screen_coord(x, y):

    # x = 1 when SCREEN_SIZE[0] / 10
    x *= GRID_SIZE
    # to have un repère orthonormé
    y *= GRID_SIZE
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
        print('wtf', line1, line2)
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
            print(x, y)
            if time < x < x_inter_min:
                x_inter_min = x
                inter_y = [y]

            elif x == x_inter_min:
                inter_y.append(y)

        time = x_inter_min
        colli += 1

        for c in crabs:
            if c.pos(time) in inter_y:
                c.collide(time)
                pos_now = c.pos_histo[-1]
                print(pos_now)

    for c in crabs:
        if c.pos_histo[-1][0] != time:
            c.pos_histo.append((time, c.pos(time)))

    return crabs


def draw_crabs(screen, crabs):
    for i, c in enumerate(crabs[::-1]):
        for A, B in segments(c.pos_histo):
            x0, y0 = to_screen_coord(*A)
            x1, y1 = to_screen_coord(*B)
            color = CRABS_COLOR[i % len(CRABS_COLOR)]
            gfxdraw.line(screen, x0, y0, x1, y1, color)
            gfxdraw.filled_circle(screen, x0, y0, 4, color)
            gfxdraw.aacircle(screen, x0, y0, 4, color)
            gfxdraw.filled_circle(screen, x1, y1, 4, color)
            gfxdraw.aacircle(screen, x1, y1, 4, color)




def run():

    with open('config.txt', 'r') as f:
        config = f.read()

    config = config.split('\n')
    crabs = []
    nb_of_crabs = int(config[0])  # int(input('number of crabs'))
    for i in range(nb_of_crabs):
        crabs.append(Crab(*map(int, config[i + 1].split())))

    crabs_save = [(c.speed, c.start) for c in crabs]

    screen = pygame.display.set_mode(SCREEN_SIZE)

    collisions = 0
    running = True
    while running:

        # read events
        for event in pygame.event.get():

            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

                if event.key == K_LEFT:
                    collisions -= 1
                    crabs = [Crab(*c) for c in crabs_save]
                    crabs = update_all_crabs(crabs, collisions)

                if event.key == K_RIGHT:
                    collisions += 1
                    crabs = [Crab(*c) for c in crabs_save]
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