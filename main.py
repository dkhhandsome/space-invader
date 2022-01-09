import pygame
import os
import time
import random
pygame.font.init()

# set the screen of game
WIDTH, HEIGHT = 750, 750
# note that tuple is similar to List but tuple is immutable and List is
# mutable.
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("space invader")

# load rival AI ship
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets",
                                                "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets",
                                                  "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets",
                                                 "pixel_ship_blue_small.png"))
# load main character
YELLOW_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
YELLOW_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_yellow.png"))

# Background for original
BG1 = pygame.image.load(os.path.join("assets", "background-black.png"))
# Background that is transformed to fill the screen
BG = pygame.transform.scale(BG1, (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        # since the laser needs to collide
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    # ?
    def off_screen(self, height):
        return not(height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:

    COOLDOWN = 30  # half a second(0.5 second since our clock for game is 60)

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        # we cannot just let the ship spams the laser we should wait half a \
        # second to let user shoot another laser.
        self.cool_down_counter = 0

    # window tells us where should we draw the ship
    def draw(self, window):
        # it means pygame will draw the rectangle and self.x and self.y \
        # indicates the position of ship and 50, 50 indicates how wide the\
        # ship will be. We can change 0 to 1 or 2 to indicate the ship will nor\
        # be filled in
        # pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 50, 50), 0)\
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            # draw lasers
            laser.draw(window)

    # two method one for checking if enemy hits the player and other check if\
    # player hits the enemy
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        # giving some time interval between laser.
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        """not sure if it works or not, """
        # get_width() can work since we have it interface
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

# Player(Ship) inherit everything (both attribute and method) from class ship.


class Player(Ship):
    def __init__(self, x, y, health=100):
        # super will get Ship's _init_ and pass the value of child's parameter\
        # in __init__ to parent's class.
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        # mask is the pygame default attribute that can help us to judge if \
        # we are in collision we hit the pixes or not.
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    # two method one for checking if enemy hits the player and other check if\
    # player hits the enemy
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    # when we need to draw something, we always put the window as parameter.

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y
                                               + self.ship_img.get_height()
                                               + 10, self.ship_img.get_width(),
                                               10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y
                                               + self.ship_img.get_height()
                                               + 10, self.ship_img.get_width()
                                               * self.health/self.max_health,
                                               10))


class Enemy(Ship):
    COLOR_MAP = {"red": (RED_SPACE_SHIP, RED_LASER),
                 "green":  (GREEN_SPACE_SHIP, GREEN_LASER),
                 "blue": (BLUE_SPACE_SHIP, BLUE_LASER)}

    # we add color there since the enemy can have different color
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        # Useful for fast pixel perfect collision detection. A mask uses 1 bit
        # per-pixel to store which parts collide.
        self.mask = pygame.mask.from_surface(self.ship_img)

    # vel indicates the speed of enemy.
    def move(self, vel):
        self.y += vel

    def shoot(self):
        # giving some time interval between laser.
        if self.cool_down_counter == 0:
            # x - 20 to make the laser shoots from the center of enemy
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    # to see if two obj is overlapping or not and if it not overlaps it will\
    # return None. And if it overlaps it will return a coordinate (x, y) to\
    # tell us where it overlaps

    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    # let game check the collision or character movement sixty times per \
    # seconds.
    fps = 60
    level = 0
    lives = 5
    # first parameter of sysfront is the name and the second is the size
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    # the List that stores enemies
    enemies = []
    # the number of enemies
    wavelength = 5
    # vel means the speed.
    enemy_vel = 1
    laser_vel = 5

    # every time press the movement key, we can move 5 pixels, which indicates\
    # the speed of player
    player_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    # when we lose the game, just pause the game and wait to restart
    lost_count = 0

    # the idea of creating a function inside function main is that redraw_\
    # window\
    #  is only applied inside the main function and it use every constant that\
    # main function gives. If it is outside we have to put the constant in \
    # main() like run and fps out side of main() which can be pretty annoying.
    def redraw_window():
        # draw the background in the up-left corner of screen
        WIN.blit(BG, (0, 0))
        # draw text
        # main_font.render means to get the font we want, and (red, green, blue)
        # stands for RGB color.
        lives_label = main_font.render(f"Lives: {lives}", True, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", True, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        # the reason put enemy.draw before the player.draw is that if we \
        # overlapping we want to see the main character first instead of \
        # enemy.
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            # pass the message to the front that we create
            lost_label = lost_font.render("You lost", True, (255, 255, 255))
            # WIDTH/2 - lost_label.get_width()/2 means we subtract extra \
            # weight from message to make it perfectly central.
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        # refresh the display of our game
        pygame.display.update()

    while run:
        # let the game follow the time given by you.
        clock.tick(fps)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            # we should understand the concept later
            if lost_count > fps * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wavelength += 5
            for i in range(wavelength):
                # random.choice is responsible for randomly choosing one of\
                # element from the List.
                enemy = Enemy(random.randrange(100, WIDTH - 100),
                              random.randrange(-1500, 100),
                              random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

        # this code means that get every event from pygame and check if them \
        # occur and do the action. Noticing that the event means such that \
        # pressing a button or start a move or losing all lives or player \
        # decide to leave the game\
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # stop running the loop
                quit()

        # get all the button we press and it is a dictionary
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            # a(left) button on my keyboard.
            # move 1 pixes to left, and make the boundary of ship \
            # following are the same way.
            player.x -= player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height()\
                + 15 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_d] and player.x + player_vel + \
                player.get_width() < WIDTH:
            # right and \
            # fixed based on the position of top-right corner(+50 since the \
            # weight of
            player.x += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        # [:] means make a copy of list of enemies in case when we modify the\
        # enemy list it will not affect our code(fix later)
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            # give the speed of laser and check if it hits the player.
            enemy.move_lasers(laser_vel, player)

            # you let the enemy have 50% chance to shoot so you choose 120 since
            # the 60 is the clock time of game.
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("press button to begin", True,
                                        (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    quit()


main_menu()


