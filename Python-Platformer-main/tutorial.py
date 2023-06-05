#importing the necessary modules and initializing the pygame module
import os 
import random
import math
import pygame
from os import listdir
from os.path import isfile, join 
pygame.init()

#setting the caption for my pygame window
pygame.display.set_caption("Space_Jump")

#defining the width & height, FPS, and the player velocity (how fast the player moves)
WIDTH, HEIGHT = 1200, 700
FPS = 60
PLAYER_VEL = 5


window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return[pygame.transform.flip(sprite, True, False)for sprite in sprites]

#function taking arguments for direction, width, and height
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        #flipping the sprite sheets by determining the direction of the player
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

#passing the size in the function
def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    #creating an image of the size
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    #Implememting the image of the image by calculating the x and y
    rect = pygame.Rect(96, 127.5, size, size)
    #blit the image to the
    surface.blit(image, (0, 0), rect)   
    return pygame.transform.scale2x(surface) 
                                
#Defining a class called Player that inherits from the pygame.sprite.Sprite class
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    #implementing gravity
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width, height):
        #Calls the constructor method of the parent class (pygame.sprite.Sprite) to initialize the player as a sprite object.
        super().__init__()
        #Creates a Pygame rectangle object that represents the player's position and dimensions.
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0 
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    #defining jump
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        
    #Updating the player's horizontal & vertical position by adding dx and dy to its current x, ycoordinate.
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0
    
    def move_left(self, vel):
        #Sets the player's horizontal velocity to -vel, which will cause it to move left.
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        #calculates vertical vel by multiplying its fall_count by the GRAVITY constant and dividing by the game's fps. 
        #takes the minimum of this value and 1 to prevent the player from falling too fast.
        #updated velocity is stored in self.y_vel.
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        # Set the default sprite sheet to "idle"
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            #implemting the sprite sheet jump and double jump depending on the jump count
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        # If the player is moving horizontally, set the sprite sheet to "run"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        if self.x_vel != 0:
            sprite_sheet = "run"
        
        # Concatenate the sprite sheet name with the player's current direction to get the name of the sprite sheet to use
        sprite_sheet_name = sprite_sheet + "_" + self.direction
            # Calculate the index of the current sprite based on the animation count and animation delay
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
   
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    #Drawing the object with the given requirements
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

#A sub class of the object class
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        #Getting a block with the given requirements
        self.image.blit(block, (0,0))
        # Setting the block's mask attribute to a new mask object created from its image surface using the pygame.mask.from_surface method
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3


    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        # Loading the sprite sheets for the fire animation
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    # Setting the animation name to "on"
    def on(self):
        self.animation_name = "on"
    
    # Set the animation name to "off"
    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)


        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    #loading image by joining the assets path, Background path, and the name of the picture I want to load
    image = pygame.image.load(join("assets", "Background", name))
    
    _, _, width, height = image.get_rect()
    tiles = []

    #using for loops to fill in the background fully with the picture
    #adding one so I don't have gaps left
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            #will denote the position, moving the position based on the foor loop 
            pos = (i * width, j * height)
            tiles.append(pos)
    
    return tiles, image

def draw(window, background, bg_image, player,  objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    # Checking for collisions between the player and each object in the list
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                # If the player is moving down and collides with an object, set its bottom to the top of the object and call its landed method
                player.rect.bottom = obj.rect.top
                # If the player is moving up and collides with an object, set its top to the bottom of the object and call its hit_head method
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            # Adding the collided object to the list of collided objects
            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    #Gets a list of all currently pressed keys using the
    keys = pygame.key.get_pressed()

    player.x_vel= 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2) 

    #Checks if the left arrow key (pygame.K_LEFT) is pressed
    if keys[pygame.K_LEFT] and not collide_left:
        #sets the player's horizontal velocity to move left
        player.move_left(PLAYER_VEL)
    #Checks if the right arrow key is pressed
    if keys[pygame.K_RIGHT] and not collide_right:
        #sets the player's horizontal velocity to move right
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

#Defines a function called main that takes a single argument called window
def main(window):
    #Creates a Pygame clock object to control the frame rate
    clock = pygame.time.Clock()
    background, bg_image = get_background("Space.png")

    block_size = 96

    player = Player(100,100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
            for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    

    #adding objects in the window according to the posistions
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), 
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire,
               Block(block_size * 4, HEIGHT - block_size * 4, block_size),
               Block(block_size * -1, HEIGHT - block_size * 3, block_size),
               Block(block_size * -1, HEIGHT - block_size * 4, block_size),
               Block(block_size * -1, HEIGHT - block_size * 5, block_size),
               Block(block_size * 7, HEIGHT - block_size * 5, block_size),
               Block(block_size * -1, HEIGHT - block_size * 2, block_size),
               Block(block_size *7, HEIGHT - block_size * 2, block_size),
               Block(block_size * 9, HEIGHT - block_size * 5, block_size),
               Block(block_size * 9, HEIGHT - block_size * 6, block_size),
               Block(block_size * 9, HEIGHT - block_size * 3, block_size),
               Block(block_size * 9, HEIGHT - block_size * 4, block_size),
               Block(block_size * 9, HEIGHT - block_size * 2, block_size),
               Block(block_size * 4, HEIGHT - block_size * 3, block_size),
               Block(block_size * 4, HEIGHT - block_size * 2, block_size),
               Block(block_size * 7, HEIGHT - block_size * 3, block_size),
               Block(block_size * -1, HEIGHT - block_size * 5, block_size),
               Block(block_size * -1, HEIGHT - block_size * 6, block_size),
               Block(block_size * -1, HEIGHT - block_size * 7, block_size),
               Block(block_size * -1, HEIGHT - block_size * 8, block_size),
               Block(block_size * 11, HEIGHT - block_size * 3, block_size),
               Block(block_size * 11, HEIGHT - block_size * 4, block_size),
               Block(block_size * 11, HEIGHT - block_size * 5, block_size),
               Block(block_size * 11, HEIGHT - block_size * 6, block_size),
               Block(block_size * 12, HEIGHT - block_size * 3, block_size),
               Block(block_size * 13, HEIGHT - block_size * 3, block_size),
               Block(block_size * 14, HEIGHT - block_size * 3, block_size),
               Block(block_size * 15, HEIGHT - block_size * 3, block_size),
               Block(block_size * 18, HEIGHT - block_size * 1, block_size),
               Block(block_size * 19, HEIGHT - block_size * 1, block_size),
               Block(block_size * 13, HEIGHT - block_size * 5, block_size),
               Block(block_size * 16, HEIGHT - block_size * 3, block_size),
               Block(block_size * 16, HEIGHT - block_size * 8, block_size),
               Block(block_size * 16, HEIGHT - block_size * 4, block_size),
               Block(block_size * 16, HEIGHT - block_size * 5, block_size),
               Block(block_size * 16, HEIGHT - block_size * 6, block_size),
               Block(block_size * 16, HEIGHT - block_size * 7, block_size),
               Block(block_size * 16, HEIGHT - block_size * 6, block_size),
               Block(block_size * 20, HEIGHT - block_size * 3, block_size),
               Block(block_size * 20, HEIGHT - block_size * 4, block_size),
               Block(block_size * 20, HEIGHT - block_size * 5, block_size),
               Block(block_size * 20, HEIGHT - block_size * 6, block_size),
               Block(block_size * 17, HEIGHT - block_size * 3, block_size),
               Block(block_size * 19, HEIGHT - block_size * 4, block_size),
               Block(block_size * 17, HEIGHT - block_size * 5, block_size),
               Block(block_size * 20, HEIGHT - block_size * 2, block_size),
               Block(block_size * 20, HEIGHT - block_size * 1, block_size),
               Block(block_size * 23, HEIGHT - block_size * 2, block_size),
               Block(block_size * 25, HEIGHT - block_size * 4, block_size),
               Block(block_size * 28, HEIGHT - block_size * 4, block_size),
               Block(block_size * 30, HEIGHT - block_size * 6, block_size),
               Block(block_size * 35, HEIGHT - block_size * 3, block_size),
               Block(block_size * 39, HEIGHT - block_size * 3, block_size),
               Block(block_size * 41, HEIGHT - block_size * 2, block_size),
               Block(block_size * 42, HEIGHT - block_size * 2, block_size),
               Block(block_size * 46, HEIGHT - block_size * 6, block_size),
               Block(block_size * 44, HEIGHT - block_size * 4, block_size),
               Block(block_size * 47, HEIGHT - block_size * 3, block_size),
               Block(block_size * 48, HEIGHT - block_size * 3, block_size),
               Block(block_size * 48, HEIGHT - block_size * 4, block_size),
               Block(block_size * 48, HEIGHT - block_size * 5, block_size),
               Block(block_size * 49, HEIGHT - block_size * 3, block_size),
               Block(block_size * 51, HEIGHT - block_size * 5, block_size),
               Block(block_size * 53, HEIGHT - block_size * 6, block_size),
               Block(block_size * 55, HEIGHT - block_size * 6, block_size),
               Block(block_size * 55, HEIGHT - block_size * 5, block_size),
               Block(block_size * 55, HEIGHT - block_size * 4, block_size),
               Block(block_size * 55, HEIGHT - block_size * 3, block_size),
               Block(block_size * 55, HEIGHT - block_size * 2, block_size),
               Block(block_size * 56, HEIGHT - block_size * 6, block_size),
               Block(block_size * 56, HEIGHT - block_size * 4, block_size),
               Block(block_size * 56, HEIGHT - block_size * 2, block_size),
               Block(block_size * 58, HEIGHT - block_size * 6, block_size),
               Block(block_size * 58, HEIGHT - block_size * 5, block_size),
               Block(block_size * 58, HEIGHT - block_size * 4, block_size),
               Block(block_size * 58, HEIGHT - block_size * 3, block_size),
               Block(block_size * 58, HEIGHT - block_size * 2, block_size),
               Block(block_size * 59, HEIGHT - block_size * 5, block_size),
               Block(block_size * 60, HEIGHT - block_size * 4, block_size),
               Block(block_size * 61, HEIGHT - block_size * 3, block_size),
               Block(block_size * 62, HEIGHT - block_size * 6, block_size),
               Block(block_size * 62, HEIGHT - block_size * 5, block_size),
               Block(block_size * 62, HEIGHT - block_size * 4, block_size),
               Block(block_size * 62, HEIGHT - block_size * 3, block_size),
               Block(block_size * 62, HEIGHT - block_size * 2, block_size),
               Block(block_size * 64, HEIGHT - block_size * 6, block_size),
               Block(block_size * 64, HEIGHT - block_size * 5, block_size),
               Block(block_size * 64, HEIGHT - block_size * 4, block_size),
               Block(block_size * 64, HEIGHT - block_size * 3, block_size),
               Block(block_size * 64, HEIGHT - block_size * 2, block_size),
               Block(block_size * 65, HEIGHT - block_size * 6, block_size),
               Block(block_size * 65, HEIGHT - block_size * 2, block_size),
               Block(block_size * 66, HEIGHT - block_size * 5, block_size),
               Block(block_size * 66, HEIGHT - block_size * 4, block_size),
               Block(block_size * 66, HEIGHT - block_size * 3, block_size),]

    offset_x = 0
    scroll_area_width = 600


    run = True
    #Begins a while loop that will continue running as long as run is True
    while run:
        #Limits the frame rate to the value stored in the constant FPS.
        clock.tick(FPS)

        #Begins a loop that checks for Pygame events
        for event in pygame.event.get():
            # Checks if the user has clicked the "X" button to close the window.
            if event.type == pygame.QUIT:
                run = False
                break

            #if the space bar key is pressed one time it will jump, if twice, it will double jump
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()

#Checks if this file is being run directly
if __name__ == "__main__":
    main(window)