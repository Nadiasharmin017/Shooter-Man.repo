import pygame
import os
from pygame.locals import *

pygame.init()
screen_width = 1000
screen_height = 700
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Shooter')

# Set framerate 
clock = pygame.time.Clock()
FPS = 60

GRAVITY = 0.75

# Define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
#load img
#bullet
bullet_img = pygame.image.load('assets/img/icons/bullet.png').convert_alpha()

#grenade
grenade_img = pygame.image.load('assets/img/icons/grenade.png').convert_alpha()


BG = (144,201,120)
RED  = (255, 0, 0)

# Function to draw the background
def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0,300),(screen_width,300))

# Soldier class for player and enemy characters
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades): 
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo =  ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []  # Initialize the list to hold animation frames
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()  # Time tracking for animation updates

        
        # load all image for the player
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            #count number of files in a folder 
            num_of_frames = len(os.listdir(f'assets/img/{self.char_type}/{animation}'))

            # Load idle animation frames
            temp_list = []  # Temporary list to hold frames for each animation
            for i in range(num_of_frames):
                img = pygame.image.load(f'assets/img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img,((img.get_width() * scale),(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)  # Add idle animation frames to the animation list
       
        # Set initial image and position
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -=1
        
    # Method to move the soldier
    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True
        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y
        #check collision with floor
        if self.rect.bottom +dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
        bullet = Bullet(self.rect.centerx+(0.6 * self.rect.size[0]* self.direction),  self.rect.centery, self.direction)
        bullet_group.add(bullet)
        #reduce ammo
        self.ammo -=1

        
    # Method to update animation frames
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.frame_index = len(self.animation_list[self.action]) -1
                else:
                  self.frame_index = 0
                
    # Method to update action
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive =False
            self.update_action(3)       
            
    # Method to draw the soldier on the screen
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x , y)
        self.direction = direction
 
    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)

        #check the bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()
            #check collision  with character
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 25
                # print(enemy.health)
                self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x , y)
        self.direction = direction
    
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #check collision with floor
        if self.rect.bottom +dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0 # granads speed
                    
        #update grenade position 
        self.rect.x += dx
        self.rect.y += dy

#crearte sprite group   
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()


# Instantiate player and enemy soldiers
player = Soldier('player', 200, 200, 3, 5,20, 5)
enemy = Soldier('enemy', 400, 200, 3, 5,20, 0)

run = True
while run:
    clock.tick(FPS)  # Control the frame rate
    
    draw_bg()  # Draw the background
    
    player.update()  # Update player animation
    player.draw()  # Draw player
    enemy.update()
    enemy.draw()  # Draw enemy

    #update and draw group
    bullet_group.update()
    grenade_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)

    
    # Update player action and movement
    if player.alive:
        if shoot:
            player.shoot()
        #throw grenade
        elif grenade and grenade_thrown == False and player.grenades > 0:
            grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] *player.direction), player.rect.top, player.direction)
            grenade_group.add(grenade)
            #reduce grenades 
            player.grenades -=1
            grenade_thrown = True
            # print(player.grenades)
        if player.in_air:
            player.update_action(2)  #2 jump
            player.move(moving_left, moving_right)

        elif moving_left or moving_right:
            player.update_action(1)  #1  run
            player.move(moving_left, moving_right)
        else:
            player.update_action(0)  #0 idle
            player.move(moving_left, moving_right)
        
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Check for quit event
            run = False
        elif event.type == pygame.KEYDOWN:  # Check for key presses
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
        elif event.type == pygame.KEYUP:  # Check for key releases
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()  # Update the display

pygame.quit()  # Quit pygame
