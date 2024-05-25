import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
Apple = pygame.image.load('resours/apple24.png')
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
GREEN = (0, 107, 60)
BLACK = (0, 0, 0)

BLOCK_SIZE = 16
SPEED = 20

input_active = False
input_text = str(SPEED)

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Змейка')
        self.clock = pygame.time.Clock()
        self.reset()
        self.walls = []

    def _generate_walls(self):
        self.walls = []
        num_walls = random.randint(3, 6)
        for _ in range(num_walls):
            wall_length = random.randint(2, 5)
            wall_x = random.randint(1, (self.w // BLOCK_SIZE) - wall_length) * BLOCK_SIZE
            wall_y = random.randint(1, (self.h // BLOCK_SIZE) - 1) * BLOCK_SIZE
            self.walls.append(pygame.Rect(wall_x, wall_y, wall_length * BLOCK_SIZE, BLOCK_SIZE))

    def reset(self):
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        self._generate_walls()

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        global SPEED, input_active, input_text
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        try:
                            SPEED = int(input_text)
                        except ValueError:
                            pass
                        input_text = str(SPEED)
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                else:
                    if event.key == pygame.K_i:
                        input_active = True

        self._move(action)
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(SPEED)
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        background_img = pygame.image.load('resours/background2.jpg')
        self.display.blit(background_img, (0, 0))

        if not self.walls:
            self._generate_walls()

        head_rect = pygame.Rect(self.snake[0].x, self.snake[0].y, BLOCK_SIZE, BLOCK_SIZE)

        for wall in self.walls:
            pygame.draw.rect(self.display, BLACK, wall)
            if head_rect.colliderect(wall):
                self.reset()
                break

        if self.direction == Direction.UP:
            head_img = pygame.image.load('resours/1.png')
            body_img = pygame.image.load('resours/2.png')
        elif self.direction == Direction.DOWN:
            head_img = pygame.image.load('resours/1.3.png')
            body_img = pygame.image.load('resours/2.png')
        elif self.direction == Direction.RIGHT:
            head_img = pygame.image.load('resours/1.2.png')
            body_img = pygame.image.load('resours/2.2.png')
        elif self.direction == Direction.LEFT:
            head_img = pygame.image.load('resours/1.4.png')
            body_img = pygame.image.load('resours/2.2.png')
        else:
            head_img = pygame.image.load('resours/1.png')
            body_img = pygame.image.load('resours/2.png')

        self.display.blit(head_img, (self.snake[0].x, self.snake[0].y))

        for pt in self.snake[1:]:
            self.display.blit(body_img, (pt.x, pt.y))

        if input_active:
            color = (0, 0, 0)
        else:
            color = (128, 128, 128)

        text_surface = font.render("Скорость: " + str(SPEED), True, color)
        self.display.blit(text_surface, (self.w - 400, 0))


        self.display.blit(Apple, (self.food.x, self.food.y))

        text = font.render("Яблок: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

