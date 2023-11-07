import pygame
import os
import random
pygame.font.init()
pygame.mixer.init()

# Constants

# Define window. Coordinate System: (0,0) is TOP LEFT. For all objects and window.
WIDTH, HEIGHT = 900, 500

# Create Window Object
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
# os.sleep(5000)

# Sets name for the window.
pygame.display.set_caption("PyGame Tutorial")

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
BLUE = (0,0,255)
GREEN = (0,255,0)

BORDER = pygame.Rect((WIDTH//2)-5, 0, 10, HEIGHT)

BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets','Grenade+1.mp3'))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets','Gun+Silencer.mp3'))

HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 80)

FPS = 60
RED_SPEED = 5
YELLOW_SPEED = 5

RED_BULLET_SPEED = 8
RED_MAX_BULLETS = 3

YELLOW_BULLET_SPEED = 8
YELLOW_MAX_BULLETS = 3

RED_HEALTH = 10
YELLOW_HEALTH = 10

SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55,40 
# '/' may be interpreted differently by different machines.
# So we use os.path.join()
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets','spaceship_yellow.png'))
# Resize the ship(inner function) then rotate it,
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH,SPACESHIP_HEIGHT)), 90)

RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets','spaceship_red.png'))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH,SPACESHIP_HEIGHT)), 270)

SPACE = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets','space.png')),(WIDTH, HEIGHT))

# Events

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

BULLET_COLLIDE = pygame.USEREVENT + 3

BOOST_TIMER = pygame.USEREVENT + 4
pygame.time.set_timer(BOOST_TIMER, 10000)

ACTIVE_BOOST_TIMER = pygame.USEREVENT + 5
pygame.time.set_timer(ACTIVE_BOOST_TIMER, 5000)

# Methods/Functions

# Using this method to draw and redraw the window every time.
def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health, boosts):
    # Order of filling matters. So background first, then each layer in front of it sequentially.

    # Colours are RGB. fill is just standard fill.
    # WIN.fill(WHITE)

    # blit is used for any text/image surface. Args: object, position
    WIN.blit(SPACE, (0,0))
    pygame.draw.rect(WIN, BLACK, BORDER)

    # Texts
    red_health_text = HEALTH_FONT.render("Health:" + str(red_health), 1, WHITE)
    yellow_health_text = HEALTH_FONT.render("Health:" + str(yellow_health), 1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 20, 10))
    WIN.blit(yellow_health_text, (10, 10))

    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))

    
    boosts.draw(WIN)
    boosts.update()

    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)
    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    # Without updating, no change in display
    pygame.display.update()

# Use these to handle ship movement. Out of bound
def yellow_handle_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x - YELLOW_SPEED > 0: # Left Key for Yellow
        yellow.x -= YELLOW_SPEED
    if keys_pressed[pygame.K_d] and yellow.x + YELLOW_SPEED + yellow.width + 5 < BORDER.x : # Right Key for Yellow
        yellow.x += YELLOW_SPEED
    if keys_pressed[pygame.K_w] and yellow.y - YELLOW_SPEED> 0: # Up Key for Yellow
        yellow.y -= YELLOW_SPEED
    if keys_pressed[pygame.K_s] and yellow.y + YELLOW_SPEED + yellow.height < HEIGHT - 15: # Down Key for Yellow
        yellow.y += YELLOW_SPEED

def red_handle_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x - RED_SPEED > BORDER.x + BORDER.width: # Left Key for Red
        red.x -= RED_SPEED
    if keys_pressed[pygame.K_RIGHT] and red.x + RED_SPEED + red.width < WIDTH: # Right Key for Red
        red.x += RED_SPEED
    if keys_pressed[pygame.K_UP] and red.y - RED_SPEED > 0: # Up Key for Red
        red.y -= RED_SPEED
    if keys_pressed[pygame.K_DOWN] and red.y + RED_SPEED + red.height < HEIGHT - 15: # Down Key for Red
        red.y += RED_SPEED

def handle_bullets(yellow_bullets, red_bullets, yellow, red):
    for bullet in yellow_bullets:
        bullet.x += YELLOW_BULLET_SPEED
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)
    
    for bullet in red_bullets:
        bullet.x -= RED_BULLET_SPEED
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)
        elif bullet.x < 0:
            red_bullets.remove(bullet)

    # Destroy bullets colliding with each other.
    for red_bullet in red_bullets:
        for yellow_bullet in yellow_bullets:
            if red_bullet.colliderect(yellow_bullet):
                pygame.event.post(pygame.event.Event(BULLET_COLLIDE))
                red_bullets.remove(red_bullet)
                yellow_bullets.remove(yellow_bullet)

class Boost(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.type = type
        if type == 'clip_boost':
            self.image = pygame.image.load(os.path.join("Assets","Boost_blue.png")).convert_alpha()
            self.color = BLUE
        elif type == 'bullet_speed_boost':
            self.image = pygame.image.load(os.path.join("Assets","Boost_red.png")).convert_alpha()
            self.color = RED
        elif type == 'repair':
            self.image = pygame.image.load(os.path.join("Assets","Boost_green.png")).convert_alpha()
            self.color = GREEN
        y_pos = random.randint(0,HEIGHT-50)
        # self.rect = pygame.Rect(BORDER.center[0]-20, y_pos, 40,30)
        self.rect = self.image.get_rect(center = (450,y_pos))

    def update(self):
        WIN.blit(self.image, self.rect)

    def check_collision(self,red_bullets, yellow_bullets):
        for bullet in red_bullets:
            if self.rect.colliderect(bullet):
                self.activate_boost("R")
        for bullet in yellow_bullets:
            if self.rect.colliderect(bullet):
                self.activate_boost("Y")

    def activate_boost(self,ship):
        if ship == 'R':
            if self.type == "clip_boost":
                RED_MAX_BULLETS += 2
            elif self.type == "bullet_speed_boost":
                RED_BULLET_SPEED += 5
            else:
                RED_HEALTH = RED_HEALTH + 5 if RED_HEALTH < 5 else 10
        if ship == 'Y':
            if self.type == "clip_boost":
                YELLOW_MAX_BULLETS += 2
            elif self.type == "bullet_speed_boost":
                YELLOW_BULLET_SPEED += 5
            else:
                YELLOW_HEALTH = YELLOW_HEALTH + 5 if YELLOW_HEALTH < 5 else 10
        pygame.event.post(pygame.event.Event(ACTIVE_BOOST_TIMER))
        self.kill()
            

def draw_winner(text):
    draw_text = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2,
                          HEIGHT//2 - draw_text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(5000)

def reset_ships():
    RED_BULLET_SPEED = 8
    RED_MAX_BULLETS = 3
    YELLOW_BULLET_SPEED = 9
    RED_MAX_BULLETS = 3

def main():
    # Rectangles(Rect) used to track ship positions
    red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    yellow = pygame.Rect(100,300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    red_bullets = []
    yellow_bullets = []

    boosts = pygame.sprite.GroupSingle()

    winner_text = ""

    # Needed for FPS maintenance.
    clock = pygame.time.Clock()

    # Game Loop/Event Loop
    run = True
    while run:
        # Makes the Game Loop run mentioned time per second.
        clock.tick(FPS)

        # List of all events happening in the environment
        for event in pygame.event.get():
            # Check if user quit the game (Close button)
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            
            # Bullets
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) <= YELLOW_MAX_BULLETS:
                    bullet = pygame.Rect(
                        yellow.x+yellow.width, yellow.y+yellow.height//2 - 2, 10, 5)
                    yellow_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

                if event.key == pygame.K_RCTRL and len(red_bullets) <= RED_MAX_BULLETS:
                    bullet = pygame.Rect(
                        red.x, red.y+red.height//2 - 2, 10, 5)
                    red_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

            if event.type == RED_HIT:
                RED_HEALTH -= 1
                BULLET_HIT_SOUND.play()

            if event.type == YELLOW_HIT:
                YELLOW_HEALTH -= 1
                BULLET_HIT_SOUND.play()

            if event.type == BULLET_COLLIDE:
                BULLET_HIT_SOUND.play()

            if event.type == BOOST_TIMER:
                boosts.add(Boost(random.choice(["clip_boost", "bullet_speed_boost", "repair"])))

            if event.type == ACTIVE_BOOST_TIMER:
                reset_ships()

        RED_BULLET_SPEED = 8
        RED_MAX_BULLETS = 3

        YELLOW_BULLET_SPEED = 8
        YELLOW_MAX_BULLETS = 3

        RED_HEALTH = 10
        YELLOW_HEALTH = 10

        if RED_HEALTH <= 0:
            winner_text = "Yellow Wins!"
        if YELLOW_HEALTH <= 0:
            winner_text = "Red Wins!"
        if winner_text != "":
            draw_winner(winner_text) # Someone Won
            break

        # print(red_bullets, yellow_bullets)
        # Tells which keys are being pressed down.
        keys_pressed = pygame.key.get_pressed()

        # Update locations for the ships
        yellow_handle_movement(keys_pressed, yellow)
        red_handle_movement(keys_pressed, red)

        handle_bullets(yellow_bullets, red_bullets, yellow, red)

        # Update Window with new values
        draw_window(red, yellow, red_bullets, yellow_bullets, RED_HEALTH, YELLOW_HEALTH, boosts)

    main()
    # pygame.quit()



# This prevents main from running if this file(module) is 
# imported by another file. Standard practice.
if __name__ == "__main__":
    main()


# Additions:-
# -Add a collision check to the bullets so if they collide, they destroy each other - DONE
# -Add power ups that you can pick up and will increase the amount of bullets you can fire, increase bullet speed etc...
# !Convert Ships to classes to make working with them easier
# :Power up stays for 5 seconds on screen. Buff duration: 5 seconds. Types: Max bullet slots - Blue, bullet speed - Red, HP restore - Green. 
# -Add a health system so you can get hit more times before you die
# -You could also add a healtbar if you're adding a healt system
# -You can also add different firing modes, like holding down a different key will shoot 2 bullets next to each other etc...
# -You could also add a border that slowly shrinks the space you can move around to prevent stalemates
# -You could add a score system