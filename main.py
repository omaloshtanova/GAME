import game
import pygame

WIDTH = 1000
HEIGHT = 1000

RACE_TIME = 60
RACE_DISTANCE_NEED = 10000

ROAD_COLOR = 116, 116, 116
LINE_COLOR = 255, 255, 255
LINE_WIDTH = 18
LINE_HEIGHT = 125

DATA_PATH = "data"
ROAD_IMAGE = "road.png"
CAR_IMAGE = "car.png"
CAR_SOUND = "car.wav"
CAR_CRASH_SOUND = "crush.mp3"
SCORE_STORAGE = "score.dat"

WHITE_BARRIER_BLOCK = (255, 115, 0), (255, 255, 255)
BLACK_BARRIER_BLOCK = (255, 200, 0), (0, 0, 0)
BARRIER_BLOCK_COLORS = [WHITE_BARRIER_BLOCK, BLACK_BARRIER_BLOCK]
BARRIER_BLOCK_MIN = 3
BARRIER_BLOCK_MAX = 6
BARRIER_INCIDENCE = 0.8  # 0 ... 1

MONEY_COLOR = 0, 115, 255
MONEY_TEXT_COLOR = 255, 255, 255
MONEY_INCIDENCE = 0.6  # 0 ... 1


def main():
    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Автогонка с препятствиями')
    pygame.mouse.set_visible(False)

    all_sprites = pygame.sprite.Group()

    red_car = game.Car(all_sprites)
    game.Road(0, all_sprites)
    game.Road(1, all_sprites)

    for i in range(5):
        game.Line(i, all_sprites)

    score = game.Score.get()
    distance = 0
    speed = 0
    game_time = 0
    game_begin = False
    game_over = False

    while True:
        tick_time = clock.get_time()
        available_time = red_car.get_available_time()

        if red_car.is_running():
            game_begin = True

        if game_begin and not game_over:
            game_time += tick_time / 1000
            distance = red_car.get_distance()

            if available_time < game_time:
                game_over = True

                if distance > score:
                    game.Score.set(distance)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    game_over and \
                    event.type == pygame.KEYDOWN and \
                    event.key == pygame.K_SPACE:
                pygame.quit()
                return

            red_car.move(event)

        screen.fill(ROAD_COLOR)

        game.build_road_object(all_sprites, distance, available_time)

        all_sprites.update(red_car.is_running())
        all_sprites.draw(screen)

        red_car.update(tick_time)
        red_car.draw(screen)

        game.print_stat(screen, game_time, distance, score)

        if game_over:
            if speed > 0:
                speed -= 3
            else:
                red_car.stop()
                success = distance >= RACE_DISTANCE_NEED
                game.level_passed(screen, success)
        else:
            speed = red_car.get_speed()

        pygame.display.flip()
        clock.tick(speed)


if __name__ == '__main__':
    main()
