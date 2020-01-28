from os import path
from main import HEIGHT
import pygame
import random

DATA_PATH = "data"
ROAD_IMAGE = "road.png"
LINE_IMAGE = "line.png"
CAR_IMAGE = "car.png"
CAR_SOUND = "car.wav"
CAR_CRASH_SOUND = "crush.mp3"
WHITE_BLOCK_IMAGE = "white_block.png"
BLACK_BLOCK_IMAGE = "black_block.png"

BLOCK_IMAGES = [WHITE_BLOCK_IMAGE, BLACK_BLOCK_IMAGE]
BLOCK_MIN = 3
BLOCK_MAX = 6


def load_image(name, colorkey=None):
    fullname = path.join(DATA_PATH, name)
    image = pygame.image.load(fullname)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    return image


def load_sound(name, volume=0.5):
    fullname = path.join(DATA_PATH, name)
    sound = pygame.mixer.Sound(fullname)
    sound.set_volume(volume)
    return sound


def play_mp3(name):
    fullname = path.join(DATA_PATH, name)
    pygame.mixer.music.load(fullname)
    pygame.mixer.music.play()


class Car:
    speedup = 60
    speedup_time = 1000  # 1 sec

    def __init__(self):
        self.image = load_image(CAR_IMAGE)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 470
        self.rect.y = 750
        self.direct_x = 0
        self.running = False
        self.speed = Car.speedup
        self.speedup_time = 0
        self.speed_sound = load_sound(CAR_SOUND)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self):
        if self.running:
            self.rect = self.rect.move(self.direct_x, 0)

    def move(self, event):
        if event.type == pygame.KEYUP:
            self.direct_x = 0
        elif event.type == pygame.KEYDOWN:
            if event.key == 275:
                self.direct_x = 1
            elif event.key == 276:
                self.direct_x = -1
            elif event.key == 273:
                self.running = True
                self.speed_sound.play(loops=-1, fade_ms=10000)

    def get_speed(self, time):
        if self.running:
            self.speedup_time += time

            if self.speedup_time > Car.speedup_time:
                self.speed += Car.speedup
                self.speedup_time = 0

        return self.speed

    def stop(self):
        self.running = False
        self.speed = Car.speedup
        self.speedup_time = 0
        self.speed_sound.stop()

    def side_crush(self):
        play_mp3(CAR_CRASH_SOUND)
        self.stop()
        self.rect = self.rect.move(10 * -self.direct_x, 0)

    def barrier_crush(self):
        play_mp3(CAR_CRASH_SOUND)
        self.stop()
        self.rect = self.rect.move(0, 10)

    #def event_loop(self, change_to):!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
     #   """Функция для отслеживания нажатий клавиш игроком"""

        # запускаем цикл по ивентам
    #    for event in pygame.event.get():
            # если нажали клавишу
        #        if event.type == pygame.KEYDOWN:
        #       if event.key == pygame.K_RIGHT or event.key == ord('d'):
        #           change_to = "RIGHT"
        #       elif event.key == pygame.K_LEFT or event.key == ord('a'):
        #           change_to = "LEFT"
        #       elif event.key == pygame.K_UP or event.key == ord('w'):
        #           change_to = "UP"
        #       elif event.key == pygame.K_DOWN or event.key == ord('s'):
        #           change_to = "DOWN"
                # нажали escape
        #       elif event.key == pygame.K_ESCAPE:
        #       elif event.key == pygame.K_ESCAPE:
        #            pygame.quit()
        #            sys.exit()
    #    return change_to)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class Road(pygame.sprite.Sprite):
    def __init__(self, num, group, car):
        super().__init__(group)
        self.car = car
        self.image = load_image(ROAD_IMAGE)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.y = -self.rect.h if num == 0 else 0

    def update(self, *args):
        if pygame.sprite.collide_mask(self, self.car):  # если объекты пересеклись по маске
            self.car.side_crush()

        if self.car.running:
            if self.rect.y == self.rect.h - 1 or self.rect.y == -1:
                self.rect.y -= self.rect.h - 1
            else:
                self.rect = self.rect.move(0, 1)


class Line(pygame.sprite.Sprite):
    def __init__(self, num, group, car):
        super().__init__(group)
        self.car = car
        self.image = load_image(LINE_IMAGE)
        self.rect = self.image.get_rect()
        self.rect.x = 491
        self.rect.y = num * self.rect.h * 2 - self.rect.h * 2

    def update(self, *args):
        if self.car.running:
            if self.rect.y == HEIGHT:
                self.rect.y = -self.rect.h * 2
            else:
                self.rect = self.rect.move(0, 1)


class BarrierBuilder:
    road_coords = {'min': 257, 'max': 731}
    block_width = 50

    def __init__(self, group, car):
        self.group = group
        self.car = car

        if random.randint(0, 1000) == 324:
            self.build()

    def build(self):
        image = BarrierBuilder.get_rand_image()
        blocks = BarrierBuilder.get_rand_blocks()
        start_x = BarrierBuilder.get_start_x(blocks)

        for i in range(blocks):
            x = start_x + i * BarrierBuilder.block_width
            BarrierBlock(self.group, self.car, image, x)

    @staticmethod
    def get_rand_image():
        return random.choice(BLOCK_IMAGES)

    @staticmethod
    def get_rand_blocks():
        return random.randint(BLOCK_MIN, BLOCK_MAX)

    @staticmethod
    def get_start_x(blocks):
        min = BarrierBuilder.road_coords['min']
        max = BarrierBuilder.road_coords['max'] - BarrierBuilder.block_width * blocks
        return random.randint(min, max)


class BarrierBlock(pygame.sprite.Sprite):
    def __init__(self, group, car, image, x):
        super().__init__(group)
        self.car = car
        self.image = load_image(image)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -self.rect.h

    def update(self, *args):
        if pygame.sprite.collide_mask(self, self.car): 
            self.remove()
            self.car.barrier_crush()

        if self.car.running:
            self.rect = self.rect.move(0, 1)

import game
import pygame

WIDTH = 1000
HEIGHT = 1000


def main():
    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('car race')
    pygame.mouse.set_visible(False)

    sprite_group = pygame.sprite.Group()

    red_car = game.Car()
    game.Road(0, sprite_group, red_car)
    game.Road(1, sprite_group, red_car)

    for i in range(5):
        game.Line(i, sprite_group, red_car)

    while True:
        screen.fill((116, 116, 116))

        game.BarrierBuilder(sprite_group, red_car)

        sprite_group.update()
        sprite_group.draw(screen)

        red_car.update()
        red_car.draw(screen)


        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            red_car.move(event)

        time = clock.get_time()
        speed = red_car.get_speed(time)
        clock.tick(speed)


if __name__ == '__main__':
    main()