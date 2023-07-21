import pygame
import math
import random
import time
import sys

pygame.init()

start_time = time.time()
count_time = time.time()
# ----------Initial Setting----------
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
MARGIN = 150
CLOSING_TIME = 2000

FPS = 60
LIVE = 3
SCORE = 0
BACK_GROUND = "#111111"
FONT = pygame.font.SysFont("Arial", 20)
LIVE_FONT = pygame.font.SysFont("Arial", 40)
FONT2 = pygame.font.SysFont("Arial", 60)
COLOR = "#F1F1F1"  # All objects are White

PADDLE_WIDTH = 120
PADDLE_HEIGHT = 15
PADDLE_SPEED = 5

BALL_RADIUS = 10
BALL_SPEED = 3
TIME_INTERVAL = 5
X_SPEED = BALL_SPEED * math.sin(50)
Y_SPEED = BALL_SPEED * math.cos(50) * -1

GAP = 4
PADDLE_GAP = 15
LINE_NUMBER = 15
ROW_NUMBER = 8
BRICK_WIDTH = (SCREEN_WIDTH - GAP) // ROW_NUMBER - GAP
BRICK_HEIGHT = 25


# ----------Draw Paddle------# ----
class Paddle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR, (self.x, self.y, self.width, self.height))

    def move(self, direction=1):
        self.x = self.x + PADDLE_SPEED * direction


# ----------Draw Ball----------
class Ball:
    x_speed = X_SPEED
    y_speed = Y_SPEED

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def ball_move(self):
        self.x += self.x_speed
        self.y += self.y_speed

    def ball_speed(self, x_speed, y_speed):
        self.x += x_speed
        self.y += y_speed

    def draw(self, screen):
        pygame.draw.circle(screen, COLOR, (self.x, self.y), self.radius)


# ----------Draw Ball----------
class Brick:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR, (self.x, self.y, BRICK_WIDTH, BRICK_HEIGHT))


# ----------Render Screen every run cycle----------
def render(game_screen, paddle, ball, brick_layout):
    global BALL_SPEED, LINE_NUMBER, PADDLE_SPEED, count_time
    games_screen.fill(BACK_GROUND)
    pygame.draw.line(games_screen, COLOR, (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT))
    paddle.draw(game_screen)
    ball.draw(game_screen)

    # ----------Draw Brick----------
    for i in range(LINE_NUMBER):
        for j in range(ROW_NUMBER):
            if brick_layout[i][j] == 1:
                create_brick(i + 1, j + 1)

    # ----------Counter----------
    message = LIVE_FONT.render(f"♥: {LIVE}", 1, "#F66666")
    games_screen.blit(message, (SCREEN_WIDTH + 45, SCREEN_HEIGHT - 100))

    message = FONT.render(f"Score:", 1, COLOR)
    games_screen.blit(message, (SCREEN_WIDTH + 29, SCREEN_HEIGHT - 130))
    message = LIVE_FONT.render(f" {SCORE}", 1, COLOR)
    games_screen.blit(message, (SCREEN_WIDTH + 78, SCREEN_HEIGHT - 147))

    message = FONT.render(f"Speed: {BALL_SPEED}", 1, COLOR)
    games_screen.blit(message, (SCREEN_WIDTH + 30, 60))

    minutes = int(time.time() - start_time) // 60
    seconds = int(time.time() - start_time) % 60
    interval = time.time() - count_time
    if LIVE > 0 and interval >= TIME_INTERVAL:
        BALL_SPEED += 1
        PADDLE_SPEED += 1
        count_time = time.time()
        LINE_NUMBER += 1
        brick_layout.insert(0, [random.randint(0, 1) for _ in range(ROW_NUMBER)])

    message = FONT.render(f"Time: {minutes}:{seconds}", 1, COLOR)
    games_screen.blit(message, (SCREEN_WIDTH + 30, 90))


# ----------Lost Game----------
def lost():
    lost_message = FONT2.render("You Lost", 1, "Red")
    lost_message_x = SCREEN_WIDTH / 2 - lost_message.get_width() / 2
    lost_message_y = SCREEN_HEIGHT / 2 - lost_message.get_height() / 2
    games_screen.blit(lost_message, (lost_message_x, lost_message_y))
    pygame.display.update()
    pygame.time.delay(CLOSING_TIME)
    sys.exit(0)


# ----------Ball Collision----------
def ball_reflect(ball,paddle,brick_layout):
    global LIVE, PADDLE_SPEED, SCORE, BALL_SPEED
    # ----------Ball collides with Wall----------
    if ball.x - BALL_RADIUS <= 0 or ball.x + BALL_RADIUS >= SCREEN_WIDTH:
        ball.x_speed *= -1
        return
    if ball.y - BALL_RADIUS <= 0:
        ball.y_speed *= -1
        return

    # ----------Ball collides with Bottom----------
    if ball.y + BALL_RADIUS >= SCREEN_HEIGHT:
        ball.y_speed = abs(ball.y_speed) * -1
        ball.x = SCREEN_WIDTH / 2
        ball.y = paddle.y - BALL_RADIUS
        paddle.x = SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2
        paddle.y = SCREEN_HEIGHT - PADDLE_HEIGHT - 5
        LIVE -= 1
        if LIVE == 0:
            lost()
        return

    # ----------Ball collides with Paddle----------
    if (paddle.x + PADDLE_WIDTH >= ball.x >= paddle.x) and (ball.y + BALL_RADIUS >= paddle.y):
        paddle_center = paddle.x + PADDLE_WIDTH / 2
        distance_to_center = ball.x - paddle_center

        percent_width = distance_to_center / paddle.width
        angle = percent_width * 90
        angle_radians = math.radians(angle)

        ball.x_speed = BALL_SPEED * math.sin(angle_radians)
        ball.y_speed = BALL_SPEED * math.cos(angle_radians) * -1

        return
    # ----------Ball collides with Brick----------
    for i in range(LINE_NUMBER):
        for j in range(ROW_NUMBER):
            if brick_layout[i][j] == 1:
                brick_left = GAP * (j + 1) + BRICK_WIDTH * j
                brick_right = GAP * (j + 1) + BRICK_WIDTH * (j + 1)
                brick_up = GAP * (i + 1) + BRICK_HEIGHT * i
                brick_down = GAP * (i + 1) + BRICK_HEIGHT * (i + 1)

                if (brick_left <= ball.x <= brick_right) and \
                        ((brick_up <= ball.y - BALL_RADIUS <= brick_down) or
                         (brick_up <= ball.y + BALL_RADIUS <= brick_down)):
                    ball.y_speed *= -1
                    brick_layout[i][j] = 0
                    SCORE += 1
                    return
                if (brick_up <= ball.y <= brick_down) and \
                        ((brick_left <= ball.x - BALL_RADIUS <= brick_right) or
                         (brick_left <= ball.x + BALL_RADIUS <= brick_right)):
                    ball.x_speed *= -1
                    brick_layout[i][j] = 0
                    SCORE += 1
                    return


# ----------Create Brick----------
def create_brick(line_number, row_number):
    brick_x = GAP * row_number + BRICK_WIDTH * (row_number - 1)
    brick_y = GAP * line_number + BRICK_HEIGHT * (line_number - 1)
    brick = Brick(brick_x, brick_y)
    brick.draw(games_screen)


# ----------Main Module----------
def main():
    # ----------Variable----------
    global LINE_NUMBER
    clock = pygame.time.Clock()

    paddle_x = SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2
    paddle_y = SCREEN_HEIGHT - PADDLE_HEIGHT - 5
    ball_x = SCREEN_WIDTH / 2
    ball_y = paddle_y - BALL_RADIUS - 20
    paddle = Paddle(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(ball_x, ball_y, BALL_RADIUS)

    brick_layout = [[random.randint(0, 1) for _ in range(ROW_NUMBER)] for _ in range(LINE_NUMBER)]

    # ----------Main loop----------
    run = True
    while run:
        # ----------Quit Event Handling----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        pygame.display.update()

        # ----------Key Press Checking----------
        keys = pygame.key.get_pressed()

        # ----------Move Paddle----------
        if keys[pygame.K_LEFT] and paddle.x >= PADDLE_GAP:
            paddle.move(-1)
        if keys[pygame.K_RIGHT] and paddle.x + paddle.width <= SCREEN_WIDTH - PADDLE_GAP:
            paddle.move(1)

        # ----------Delete Blank Line----------
        i = len(brick_layout) - 1
        while i >= 0 and all(element == 0 for element in brick_layout[i]):
            brick_layout.pop(i)
            LINE_NUMBER -= 1
            i -= 1
        if LINE_NUMBER > SCREEN_HEIGHT // (BRICK_HEIGHT + GAP):
            lost()

        # ----------Render Object----------
        render(games_screen, paddle, ball, brick_layout)
        ball.ball_move()
        ball_reflect(ball,paddle,brick_layout)

        # ----------Define FPS----------
        clock.tick(FPS)


# ----------Main Program----------
pygame.display.set_caption("Brick Breaker")
games_screen = pygame.display.set_mode((SCREEN_WIDTH + MARGIN, SCREEN_HEIGHT))

if __name__ == "__main__":
    main()
