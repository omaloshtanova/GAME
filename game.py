from os import path
from main import *
import pygame
import random


def load_image(name, color_key=None):
    fullname = path.join(DATA_PATH, name)
    image = pygame.image.load(fullname)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
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


def print_stat(surface, time, distance, score, x=20, y=20, color=(255, 255, 255), bg_color=(0, 0, 0)):
    pygame.draw.rect(surface, bg_color, (x, y, 205, 100))
    font = pygame.font.SysFont(None, 30)
    time_text = font.render(f"Время гонки: {int(time)}", 1, color)
    surface.blit(time_text, (x + 15, y + 10))
    distance_text = font.render(f"Расстояние: {int(distance)}", 1, color)
    surface.blit(distance_text, (x + 15, y + 40))
    score_text = font.render(f"Рекорд: {score}", 1, color)
    surface.blit(score_text, (x + 15, y + 70))


def level_passed(surface, success):
    if success:
        header = 'Уровень пройден'
        message = 'для продолжения нажмите пробел'
    else:
        header = 'Игра окончена'
        message = 'для выхода нажмите пробел'

    header_font = pygame.font.Font(None, 80)
    message_font = pygame.font.Font(None, 40)
    header_text = header_font.render(header, 1, (255, 255, 255))
    message_text = message_font.render(message, 1, (255, 255, 255))

    window_width = 600
    window_height = 250
    window_x = WIDTH // 2 - window_width // 2
    window_y = HEIGHT // 2 - window_height // 2
    window_border_shift = 30
    header_text_x = WIDTH // 2 - header_text.get_width() // 2
    message_text_x = WIDTH // 2 - message_text.get_width() // 2

    pygame.draw.rect(surface, (0, 0, 0),
                     (window_x, window_y, window_width, window_height))
    pygame.draw.rect(surface, (255, 255, 255),
                     (window_x + window_border_shift, window_y + window_border_shift, window_width
                      - window_border_shift * 2, window_height - window_border_shift * 2), 3)
    surface.blit(header_text, (header_text_x, window_y + 60))
    surface.blit(message_text, (message_text_x, window_y + 150))


def build_road_object(group, current_distance, available_time):
    if current_distance - ObjectBuilder.last_distance > ObjectBuilder.barrier_distance_min:
        bonus_time = RACE_TIME * 2 - available_time
        max = int(1000 * (1 - MONEY_INCIDENCE))
        choice = random.randint(0, max)

        if bonus_time > 0 and choice == 0:
            ObjectBuilder.last_distance += ObjectBuilder.money_distance_min
            ObjectBuilder.build_money(group)
        else:
            max = int(1000 * (1 - BARRIER_INCIDENCE))
            choice = random.randint(0, max)

            if choice in [0, max]:
                ObjectBuilder.last_distance = current_distance
                ObjectBuilder.build_barrier(group)


class Car:
    timeup = 10
    speedup = 25
    speedup_time = 1000  # 1 sec

    def __init__(self, group):
        self.group = group
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
        self.available_time = RACE_TIME
        self.distance = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, time):
        self.crush_check()

        if self.running:
            self.rect = self.rect.move(self.direct_x, 0)

            self.distance += 1
            self.speedup_time += time

            if self.speedup_time > Car.speedup_time:
                self.speed += Car.speedup
                self.speedup_time = 0

                # Чтобы величина скорости росла, но не уходила в бесконечность
                correct_speed = pygame.time.Clock().get_fps()
                if self.speed - 500 > correct_speed:
                    self.speed = correct_speed + 500

    def move(self, event):
        if event.type == pygame.KEYUP:
            self.direct_x = 0
        elif event.type == pygame.KEYDOWN:
            if event.key == 275:
                self.direct_x = 1
            elif event.key == 276:
                self.direct_x = -1
            elif event.key == 273:
                self.run()

    def run(self):
        self.running = True
        self.speed_sound.play(loops=-1, fade_ms=10000)

    def is_running(self):
        return self.running

    def get_distance(self):
        return self.distance

    def get_speed(self):
        return self.speed

    def get_available_time(self):
        return self.available_time

    def add_time(self):
        self.available_time += Car.timeup

    def stop(self):
        self.running = False
        self.speed = Car.speedup
        self.speedup_time = 0
        self.speed_sound.stop()

    def crush_check(self):
        for sprite in self.group.sprites():
            # если объект типа Barrier и он пересекся с машиной
            if isinstance(sprite, Barrier) and pygame.sprite.collide_rect(self, sprite):
                sprite.kill()
                self.barrier_crush()
            # если объект типа TimeMoney и он пересекся с машиной
            elif isinstance(sprite, TimeMoney) and pygame.sprite.collide_rect(self, sprite):
                sprite.hide()
                self.add_time()
            # если объект типа Road и пересеклись по маске
            elif isinstance(sprite, Road) and pygame.sprite.collide_mask(self, sprite):
                self.road_crush()

    def road_crush(self):
        play_mp3(CAR_CRASH_SOUND)
        self.stop()
        self.rect = self.rect.move(10 * -self.direct_x, 0)

    def barrier_crush(self):
        play_mp3(CAR_CRASH_SOUND)
        self.stop()
        self.rect = self.rect.move(0, 10)


class Road(pygame.sprite.Sprite):
    coord_min = 271
    coord_max = 740

    def __init__(self, num, group):
        super().__init__(group)
        self.image = load_image(ROAD_IMAGE)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.y = -self.rect.h if num == 0 else 0

    def update(self, is_running, *args):
        if is_running:
            if self.rect.y == self.rect.h - 1 or self.rect.y == -1:
                self.rect.y -= self.rect.h - 1
            else:
                self.rect = self.rect.move(0, 1)


class Line(pygame.sprite.Sprite):
    def __init__(self, num, group):
        super().__init__(group)
        self.image = pygame.Surface([LINE_WIDTH, LINE_HEIGHT])
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, LINE_COLOR, self.rect)
        self.rect.x = 491
        self.rect.y = num * self.rect.h * 2 - self.rect.h * 2

    def update(self, is_running, *args):
        if is_running:
            if self.rect.y == HEIGHT:
                self.rect.y = -self.rect.h * 2
            else:
                self.rect = self.rect.move(0, 1)


class ObjectBuilder:
    last_distance = 0
    barrier_distance_min = 400
    money_distance_min = 200

    @staticmethod
    def build_money(group):
        x = ObjectBuilder.get_x(TimeMoney.circle_radius * 2)
        TimeMoney(group, x)

    @staticmethod
    def build_barrier(group):
        colors = ObjectBuilder.get_rand_colors()
        blocks = ObjectBuilder.get_rand_blocks()
        start_x = ObjectBuilder.get_x(Barrier.block_width * blocks)
        Barrier(group, colors, blocks, start_x)

    @staticmethod
    def get_rand_colors():
        return random.choice(BARRIER_BLOCK_COLORS)

    @staticmethod
    def get_rand_blocks():
        return random.randint(BARRIER_BLOCK_MIN, BARRIER_BLOCK_MAX)

    @staticmethod
    def get_x(width):
        return random.randint(Road.coord_min, Road.coord_max - width)


class Barrier(pygame.sprite.Sprite):
    block_width = 50
    block_height = 40
    block_border_coords = [(0, 40), (25, 0), (50, 0), (25, 40)]

    def __init__(self, group, colors, blocks, x):
        super().__init__(group)
        self.image = pygame.Surface([Barrier.block_width * blocks, Barrier.block_height])
        self.draw_image(colors, blocks)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -self.rect.h

    def draw_image(self, color, blocks):
        pygame.draw.rect(self.image, color[0], self.image.get_rect())

        for b in range(blocks):
            pygame.draw.polygon(self.image, color[1], Barrier.get_block_coords(b))

    @staticmethod
    def get_block_coords(num):
        coords = []
        for c in Barrier.block_border_coords:
            coords.append((c[0] + Barrier.block_width * num, c[1]))

        return coords

    def update(self, is_running, *args):
        if is_running:
            self.rect = self.rect.move(0, 1)


class TimeMoney(pygame.sprite.Sprite):
    circle_radius = 35
    circle_text = f'+{Car.timeup}'
    circle_text_size = 35

    def __init__(self, group, x):
        super().__init__(group)
        radius = TimeMoney.circle_radius
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.draw_image(radius)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -self.rect.h
        self.hidden = False

    def draw_image(self, radius):
        pygame.draw.circle(self.image, MONEY_COLOR, (radius, radius), radius)
        self.image.set_colorkey((0, 0, 0))
        font = pygame.font.SysFont(None, TimeMoney.circle_text_size)
        text = font.render(TimeMoney.circle_text, 1, MONEY_TEXT_COLOR)
        text_x = radius - text.get_width() // 2
        text_y = radius - text.get_height() // 2
        self.image.blit(text, (text_x - 2, text_y))

    def hide(self):
        self.hidden = True

    def update(self, is_running, *args):
        if self.hidden:
            if self.rect.y + self.rect.h < 0:
                self.kill()
            else:
                self.rect = self.rect.move(0, -3)
        elif is_running:
            self.rect = self.rect.move(0, 1)


class Score:
    storage = path.join(DATA_PATH, SCORE_STORAGE)

    @staticmethod
    def set(score):
        file = open(Score.storage, 'w')
        file.write(str(score))
        file.close()

    @staticmethod
    def get():
        if path.exists(Score.storage):
            file = open(Score.storage, 'r')
            score = int(file.readline())
            file.close()
        else:
            score = 0

        return score
