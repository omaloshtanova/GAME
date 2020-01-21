from os import path
import pygame


def load_image(name, colorkey=None):
    fullname = path.join('data', name)
    image = pygame.image.load(fullname)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    return image


class Car(pygame.sprite.Sprite):

    def __init__(self, group, road_width):
        super().__init__(group)
        self.image = load_image("car.png")
        self.rect = self.image.get_rect()
        print(self.rect)
        self.rect.x = 500 - self.rect.x
        self.rect.y = 750
        self.direct_x = 0

    def update(self, *args):
        self.rect = self.rect.move(self.direct_x, 0)

    def move(self, event):
        if event.type == pygame.KEYUP:
            self.direct_x = 0
        elif event.type == pygame.KEYDOWN:
            if event.key == 275:
                self.direct_x = 1
            elif event.key == 276:
                self.direct_x = -1


pygame.init()

clock = pygame.time.Clock()
time = 0
tick = 100

size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)

image = load_image("road.png")
y = 0

car_sprite = pygame.sprite.Group()
car_sprite.draw(screen)
red_car = Car(car_sprite, 470)

running = True

while running:
    screen.blit(image, (0, y - 1826))
    screen.blit(image, (0, y))
    car_sprite.draw(screen)
    car_sprite.update()

    pygame.display.flip()
    y += 1

    if y == 1826:
        y = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        red_car.move(event)

    clock.tick(tick)
    time += clock.get_time()

    if time > 1000:
        tick += 10
        time = 0

pygame.quit()
