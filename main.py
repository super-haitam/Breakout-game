import random
import pygame
import sys
sys.path.append("/game_touches_help")
from game_touches_help.get_game_touches_help_img import CreateImage, get_pygame_img
from levels import levels_list
pygame.init()
pygame.font.init()


# Screen
WIDTH, HEIGHT = 700, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Break-out")

# FPS
clock = pygame.time.Clock()
FPS = 60

# Colors
PSEUDO_WHITE = tuple(random.randint(200, 255) for _ in range(3))
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
DARK_BLUE = (0, 0, 95)
GREY = (90, 90, 90)
LIGHT_GREY = (180, 180, 180)

# Vars
block_w = block_h = 50
power_ups_list = ["life", "ball", "length", "fire"]
power_ups_vel = 2
length_all_power_ups = 0
fire_vel = 3


# Ctrl Touches help img
move_player_img = get_pygame_img(CreateImage(PSEUDO_WHITE, {"Move Player": ["left", "right"]}))
release_ball_img = get_pygame_img(CreateImage(PSEUDO_WHITE, {"Release Ball": "space"}))
w = WIDTH/7
move_player_img = pygame.transform.scale(move_player_img,
                                         (w, (move_player_img.get_height()*w)/move_player_img.get_width()))
release_ball_img = pygame.transform.scale(release_ball_img,
                                          (w, (release_ball_img.get_height()*w)/release_ball_img.get_width()))


# Classes
class Player:
    def __init__(self, color, vel):
        self.color = color
        self.vel = vel

        self.width = self.original_w = 75
        self.redefine_rect((WIDTH - self.width) / 2, HEIGHT * (8/9))

        self.life = 5
        self.laser_num = 0

    def handle_movement(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_RIGHT] and self.rect.x + self.rect.w + self.vel <= WIDTH:
            self.rect.x += self.vel
        if pressed_keys[pygame.K_LEFT] and 0 <= self.rect.x - self.vel:
            self.rect.x -= self.vel

    def redefine_rect(self, x, y):
        height = 15
        self.rect = pygame.Rect([x, y, self.width, height])

    def handle_powerup_collision(self):
        global length_all_power_ups
        for num, power_up in enumerate(all_power_ups):
            if self.rect.colliderect(power_up.rect):
                apply_power_up(power_up.power_up_str)
                all_power_ups.pop(num)
                length_all_power_ups -= 1
                break
            elif power_up.rect.y > HEIGHT:
                all_power_ups.pop(num)
                length_all_power_ups -= 1
        self.redefine_rect(self.rect.x, self.rect.y)

    def draw_laser(self):
        for i in range(self.laser_num):
            screen.blit(
                pygame.transform.scale(pygame.image.load("assets/laser.png"), (balls[0].radius, balls[0].radius)),
                (self.rect.x + self.width / (self.laser_num+1) * (i+1) - balls[0].radius/2,
                 self.rect.y - balls[0].radius/2))

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

        self.draw_laser()


class Ball:
    def __init__(self, speed):
        self.radius = 14

        self.image = pygame.transform.scale(pygame.image.load("assets/ball.png"), (self.radius, self.radius))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = player.rect.x + player.rect.w / 2 - self.radius/2, player.rect.y - player.rect.h / 2

        self.speed = speed

        self.speed_x = random.choice([-1, 1])
        self.speed_y = -1

    def move(self):
        self.rect.x += self.speed * self.speed_x
        self.rect.y += self.speed * self.speed_y

    def bounce(self, axis: str):
        if axis == 'x':
            self.speed_x *= -1
        elif axis == 'y':
            self.speed_y *= -1

    def handle_collision_place(self, rect: pygame.Rect):
        x_points_list = [(rect.topleft[0], rect.topleft[1] + _) for _ in range(rect.h)] +\
                        [(rect.topright[0], rect.topright[1] + _) for _ in range(rect.h)]
        y_points_list = [(rect.topleft[0] + _, rect.topleft[1]) for _ in range(rect.w)] + \
                        [(rect.bottomleft[0] + _, rect.bottomleft[1]) for _ in range(rect.w)]
        points_list = x_points_list + y_points_list

        for num, point in enumerate(points_list):
            if self.rect.collidepoint(point[0], point[1]):
                if num < len(x_points_list):
                    self.bounce('x')
                else:
                    self.bounce('y')
                break

    def handle_collision(self):
        global length_all_power_ups

        for blocks_num, blocks_list in enumerate(collision_group):
            for num, block in enumerate(blocks_list):
                if block:
                    if self.rect.colliderect(block.rect):
                        self.handle_collision_place(block.rect)
                        collision_group[blocks_num][num] = None
                        if block.power_up_str:
                            all_power_up_blocks.append(block)
                            length_all_power_ups += 1

        if self.rect.colliderect(player.rect) and self.speed_y > 0:
            self.bounce('y')

    def handle_movement(self):
        self.move()

        if not 0 < self.rect.x < WIDTH:
            self.bounce('x')

        if not 0 < self.rect.y:
            self.bounce('y')

        if not self.rect.y < HEIGHT:
            balls.pop(balls.index(self))

        self.handle_collision()

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Block:
    def __init__(self, color, x, y):
        self.color = color
        self.rect = pygame.Rect([x, y, block_w, block_h])
        self.get_power_up()

    def get_power_up(self):
        self.power_up_str = None
        if random.choice([0, 0, 1]):
            self.power_up_str = random.choice(power_ups_list)

    def __repr__(self):
        return "Block"


class PowerUp:
    def __init__(self, power_up_str: str, x, y):
        self.power_up_str = power_up_str

        self.image = pygame.transform.scale(pygame.image.load(f"assets/{power_up_str}.png"), (20, 20))
        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = x, y
        
    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def __repr__(self):
        return "PowerUp"


class Fire:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("assets/fire.png"), (balls[0].radius, balls[0].radius))
        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = x, y
        self.distance_from_x = self.rect.x - player.rect.x

    def reset_pos(self):
        self.rect.x = player.rect.x + self.distance_from_x
        self.rect.y = player.rect.y - balls[0].radius / 2

    def handle_collision(self):
        global length_all_power_ups
        for num_block_list, block_list in enumerate(all_blocks_list):
            for num_block, block in enumerate(block_list):
                if block:
                    if self.rect.colliderect(block.rect):
                        all_blocks_list[num_block_list][num_block] = None
                        if block.power_up_str:
                            all_power_up_blocks.append(block)
                            length_all_power_ups += 1
                        self.reset_pos()

    def handle_out(self):
        if self.rect.y < 0:
            self.reset_pos()

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


# Functions
def random_color(a, b):
    return tuple(random.randint(a, b) for _ in range(3))


def apply_power_up(power_up_str: str):
    if power_up_str == "life":
        player.life += 1
    elif power_up_str == "ball":
        balls.append(Ball(5))
    elif power_up_str == "length":
        player.width += 10
        for i in range(player.laser_num):
                fire_list[i].distance_from_x = player.width / (player.laser_num+1) * (i+1) - balls[0].radius/2
    elif power_up_str == "fire":
        player.laser_num += 1
        for i in range(player.laser_num):
            if i == player.laser_num-1:
                fire_list.append(Fire(player.rect.x + player.width / (player.laser_num+1) * (i+1) - balls[0].radius/2,
                                      player.rect.y - balls[0].radius/2))
            else:
                fire_list[i].distance_from_x = player.width / (player.laser_num+1) * (i+1) - balls[0].radius/2


def draw_welcome():
    screen.fill(PSEUDO_WHITE)

    font = pygame.font.SysFont("comicsans", 80)
    wlcmto_txt = font.render("WELCOME TO", True, BLACK)
    game_name_txt = font.render(pygame.display.get_caption()[0], True, random_color(0, 255))
    game_txt = font.render("GAME", True, BLACK)

    screen.blit(wlcmto_txt, ((WIDTH-wlcmto_txt.get_width())/2, HEIGHT/8))
    screen.blit(game_name_txt, ((WIDTH-game_name_txt.get_width())/2, HEIGHT*(1/2-1/9)))
    screen.blit(game_txt, ((WIDTH-game_txt.get_width())/2, HEIGHT*(2/3)))

    # Blit ctrl touches
    offset = WIDTH/18
    screen.blit(release_ball_img, (offset, HEIGHT/2))
    screen.blit(move_player_img, (WIDTH-offset-move_player_img.get_width(), HEIGHT/2))

    pygame.display.flip()


def draw_new_level():
    def get_level_list():
        level_list = []
        li = []
        for i in levels_list[level_num]:
            if i == '\n':
                level_list.append(''.join(li))
                li = []
            else:
                li.append(i)
        return level_list[1:]

    level_list = get_level_list()

    num_in_x = len(level_list[0])
    num_in_y = len(level_list)
    for num_block_list, block_list in enumerate(level_list):
        li = []
        for num_block, block in enumerate(block_list):
            if block == 'B':
                li.append(Block(random_color(0, 255), num_block / num_in_x * WIDTH*(19/20) + WIDTH/4 / num_in_x,
                                num_block_list / num_in_y * HEIGHT*(1/2) + 30))
                pygame.draw.rect(screen, li[num_block].color, li[num_block].rect)
            else:
                li.append(None)
        all_blocks_list.append(li)


def draw_level():
    for block_list in all_blocks_list:
        for block in block_list:
            if block:
                pygame.draw.rect(screen, block.color, block.rect)


def level_finished():
    empty = True
    for block_list in all_blocks_list:
        for block in block_list:
            if block:
                empty = False

    if empty:
        return True
    return False


def update_power_ups():
    global length_all_power_ups
    if all_power_up_blocks:
        block = all_power_up_blocks[-1]
        if length_all_power_ups > len(all_power_ups):
            all_power_ups.append(PowerUp(block.power_up_str,  # power up: str
                                         block.rect.x + block_w / 2,  # x
                                         block.rect.y + block_h / 2))  # y
            length_all_power_ups -= 1


def draw_loosing():
    screen.fill(PSEUDO_WHITE)

    font = pygame.font.SysFont("comicsans", 80)
    txt = font.render("YOU LOST !", True, BLACK)
    screen.blit(txt, ((WIDTH-txt.get_width())/2, (HEIGHT-txt.get_height())/2))

    pygame.display.flip()


def draw_winning():
    screen.fill(PSEUDO_WHITE)

    font = pygame.font.SysFont("comicsans", 80)
    txt = font.render("YOU WON !", True, BLACK)
    screen.blit(txt, ((WIDTH-txt.get_width())/2, (HEIGHT-txt.get_height())/2))

    pygame.display.flip()


def draw_screen():
    global timer
    timer -= 1
    screen.fill(DARK_BLUE)

    font = pygame.font.SysFont("comicsans", 20)
    life_txt = font.render(f"life: {player.life}", True, WHITE)
    level_txt = font.render(f"level: {level_num+1}", True, WHITE)
    balls_txt = font.render(f"balls: {len(balls)}", True, WHITE)
    screen.blit(life_txt, (10, 0))
    screen.blit(level_txt, ((WIDTH-level_txt.get_width())/2, 0))
    screen.blit(balls_txt, (WIDTH-balls_txt.get_width()-10, 0))

    if new_level:
        draw_new_level()
    else:
        draw_level()

    player.draw()
    for ball in balls:
        ball.draw()

    for power_up in all_power_ups:
        power_up.rect.y += power_ups_vel
        power_up.draw()

    for fire in fire_list:
        fire.rect.y -= fire_vel
        fire.handle_collision()
        fire.handle_out()
        fire.draw()

    pygame.display.flip()


# Instances
player = Player(GREY, 8)
balls = [Ball(5)]

# Vars
collision_group = []
all_blocks_list = []
all_power_up_blocks = []
all_power_ups = []
fire_list = []

# Mainloop
dont_pay_attention = 0
new_level = True
level_num = 0
is_started = False
running = True
ball_stick = True
timer = 60
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

        if event.type == pygame.MOUSEBUTTONDOWN and not is_started:
            is_started = True

        if pygame.key.get_pressed()[pygame.K_SPACE] and ball_stick:
            ball_stick = False

    if not is_started:
        draw_welcome()
        continue

    player.handle_movement()

    if ball_stick:
        balls[0].rect.x, balls[0].rect.y = player.rect.x + player.rect.w / 2 - balls[0].radius / 2,\
                                           player.rect.y - player.rect.h / 2
    else:
        for ball in balls:
            ball.handle_movement()

    collision_group = all_blocks_list
    
    update_power_ups()
    player.handle_powerup_collision()

    if level_num == len(levels_list):
        pygame.time.wait(1200)

        draw_winning()

        pygame.time.wait(2000)

        is_started = False
        level_num = 0
        player.life = 5
        all_blocks_list = []
        balls = [Ball(5)]

    # THE balls are gone LMAO
    if not balls:
        if player.life:
            balls.append(Ball(5))  # Or balls = [Ball(5)] is the same cuz balls == []
            player.life -= 1
            ball_stick = True
        else:
            pygame.time.wait(1200)

            draw_loosing()

            pygame.time.wait(2000)

            is_started = False
            level_num = -1
            player.life = 5
            all_blocks_list = []
            balls = [Ball(5)]

    draw_screen()

    new_level = False
    if level_finished():
        level_num += 1
        new_level = True
        ball_stick = True
        balls = [Ball(5)]
        all_power_up_blocks = []
        all_power_ups = []
        player.width = player.original_w
        player.laser_num = 0
        fire_list = []
    dont_pay_attention += 1
