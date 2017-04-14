import collections
import pygame
from pygame import gfxdraw
from pygame.locals import *

pygame.init()
pygame.key.set_repeat(100)

WHITE = (255, 255, 255)
GREY_25 = (183, 183, 183)
BLACK = (0, 0, 0)

SCREEN_SIZE = (500, 400)
GRID_SIZE = SCREEN_SIZE[1] // 16


class Crab:
    def __init__(self, start, speed):
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
    for c in crabs:
        for A, B in segments(c.pos_histo):
            x0, y0 = to_screen_coord(*A)
            x1, y1 = to_screen_coord(*B)
            gfxdraw.line(screen, x0, y0, x1, y1, BLACK)


def run():
    nb_of_crabs = 3  # int(input('number of crabs'))
    crabs = [(0, 0)] * nb_of_crabs
    # for i in range(nb_of_crabs):
    #     start, speed = map(int, input('Starting point, speed: ').split())
    #     crabs[i] = start, speed
    crabs = [Crab(1, 2),
             Crab(3, 0),
             Crab(-1, -2)]

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