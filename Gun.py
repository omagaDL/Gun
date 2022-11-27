import math
import time
from random import choice
from random import randint

import pygame


FPS = 30

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600


class Ball:
    def __init__(self, screen: pygame.Surface, x = WIDTH * 0.5, y = 450):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.live = 30
        self.time = 0
        self.ballbust = 0
        self.is_moving = True

    def move(self, dt = 1):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        if self.y <= 550:
            self.vy -= 1.2 * dt
            self.y -= self.vy * dt
            self.x += self.vx * dt
            self.vx *= 0.99
        else:
            if self.vx ** 2 + self.vy ** 2 > 10:
                self.vy = -self.vy / 2
                self.vx = self.vx / 2
                self.y = 549
            else:
                self.is_moving = False

        if self.x > 780:
            self.vx = -self.vx / 2
            self.x = 779


    def draw(self):
        if self.is_moving == False:
            self.ballbust += 1
        if self.ballbust >= 30:
            self.color = WHITE
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )


    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """

        if (self.x - obj.x) ** 2 + (self.y - obj.y) ** 2 <= (self.r + obj.r + 30) ** 2:
            return True
        return False


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 30
        self.f2_on = 0
        self.an = 1
        self.color = YELLOW
        self.x = WIDTH/2
        self.y = 450
        self.speed = 2

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen, self.x, self.y)
        new_ball.r += 5
        self.an = math.atan2((event.pos[1]-self.y), (event.pos[0]-self.x))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = - self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 30

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            if event.pos[0]-self.x != 0:
                self.an = math.atan((event.pos[1]-self.y) / (event.pos[0]-self.x))
            else:
                self.an = math.atan((event.pos[1] - self.y) / 0.0001)
        if self.f2_on:
            self.color = RED
        else:
            self.color = YELLOW

    def draw(self):
        gun_w = 10
        gun_l = self.f2_power
        x0, y0 = pygame.mouse.get_pos()

        sin_an = math.sin(self.an)
        cos_an = math.cos(self.an)
        if self.x > x0:
            sin_an = -sin_an
            cos_an = -cos_an
        coords = [(self.x + gun_w * 0.5 * sin_an, self.y - gun_w * 0.5 * cos_an),
                  (self.x + gun_w * 0.5 * sin_an + gun_l * cos_an, self.y - gun_w * 0.5 * cos_an + gun_l * sin_an),
                  (self.x - gun_w * 0.5 * sin_an + gun_l * cos_an, self.y + gun_w * 0.5 * cos_an + gun_l * sin_an),
                  (self.x - gun_w * 0.5 * sin_an, self.y + gun_w * 0.5 * cos_an)]

        pygame.draw.polygon(screen, self.color, coords)
        pygame.draw.polygon(screen, YELLOW, [(self.x - 30, self.y + 25), (self.x + 30, self.y + 25),
                                             (self.x + 50, self.y + 5), (self.x - 50, self.y + 5)])
        pygame.draw.circle(screen, YELLOW, [self.x, self.y + 5], 15)



    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = YELLOW

    def gun_move(self, event):
        if (pygame.key.get_pressed()[pygame.K_d]) and (self.x <= WIDTH -30):
            self.x += 10
        elif (pygame.key.get_pressed()[pygame.K_a]) and (self.x >= 30):
            self.x -= 10

class Target:
    def __init__(self, a = 0):

        self.points = 0
        self.cnt = 0
        self.live = 1
        self.new_target(a)

    def new_target(self, v, clr = RED):
        """ Инициализация новой цели. """
        self.x = randint(20, 780)
        self.y = randint(50, 200)
        self.r = randint(7, 20)
        self.v = v
        self.live = 1
        self.color = clr



    def move(self):
        if (self.x + self.v > 750) or (self.x + self.v < 50):
            print(self.x - self.v, self.v)
            self.v = -self.v
        self.x += self.v

    def drop(self):
        global bombs
        b = Bomb(self.x, self.y)
        bombs.append(b)



    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.points += points

    def draw(self):
        self.cnt += 1
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.r)

class Bomb:
    def __init__(self, x_targ, y_targ):
        self.live = 1
        self.color = GREY
        self.x = x_targ
        self.y = y_targ
        self.r = 7

    def move(self):
        self.y += 1

    def hit(self, obj):
        if (self.x - obj.x) ** 2 + (self.y - obj.y) ** 2 <= (self.r + obj.r + 30) ** 2:
            return True
        return False

    def hit(self):
        self.color = BLACK
        self.y += 300

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 7)

    def BOOM(self, obj):
        if (obj.x - self.x) ** 2 + (obj.y - self.y) ** 2 <= 400:
            return True
        return False


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []
bombs = []

clock = pygame.time.Clock()
gun = Gun(screen)
target = Target()
extrtarget = Target()
finished = False
a = 0

while not finished:
    screen.fill(WHITE)
    gun.draw()
    target.draw()
    extrtarget.draw()
    for bmb in bombs:
        bmb.draw()
    for b in balls:
        b.draw()
    pygame.display.update()

    clock.tick(FPS)
    if (pygame.key.get_pressed()[pygame.K_d]) or (pygame.key.get_pressed()[pygame.K_a]):
        gun.gun_move(event)
    for event in pygame.event.get():
        #gun.gun_move(event)
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)


    for b in balls:
        for bmb in bombs:
            bmb.move()
            if b.hittest(bmb):
                bmb.live = 0
                bmb.hit()
            if bmb.BOOM(gun):
                time.sleep(1)
                finished = True
        b.move()
        if b.hittest(target) and target.live:
            target.live = 0
            target.hit()
            target.new_target(0)
        if b.hittest(extrtarget) and extrtarget.live:
            extrtarget.live = 0
            extrtarget.hit()
            extrtarget.new_target(randint(7, 13), GREY)


    extrtarget.move()
    if randint(0, 100) > 98:
        extrtarget.drop()
    gun.power_up()

pygame.quit()