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
