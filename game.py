from __future__ import division
import pygame
import sys
import math
import random
import sys

class Vector:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
    
    def getMagnitude(self):
        return math.sqrt(self.x**2+self.y**2)

    def normalize(self):
        try:
            return Vector(self.x/self.getMagnitude(),
                          self.y/self.getMagnitude())
        except ZeroDivisionError:
            return Vector()

    def __sub__(self,other):
        if isinstance(other,Vector):
            return Vector(self.x-other.x,self.y-other.y)
        else:
            raise TypeError

    def __add__(self,other):
        if isinstance(other,Vector):
            return Vector(self.x+other.x,self.y+other.y)
        else:
            raise TypeError
    def __radd__(self,other):
        return self.__add__(other)

    def __mul__(self,other):
        if isinstance(other,Vector):
            return Vector(self.x*other.x,self.y*other.y)
        else:
            return Vector(self.x*other,self.y*other)
    def __rmul__(self,other):
        return self.__mul__(other)
        
    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+")"
        
    def __eq__(self,other):
        try:
            if self.x == other.x and self.y == other.y:
                return True
            else:
                return False
        except:
            return False
    def __req__(self,other):
        return self.__eq__(other)
    
    def __ne__(self,other):
        try:
            if self.x != other.x or self.y != other.y:
                return True
            else:
                return False
        except:
            return False

    def dot(a,b):
        if not isinstance(a,Vector) or not isinstance(b,Vector):
            raise TypeError
        return a.x*b.x + a.y*b.y    

class Entity(object):
    def __init__(self,sprite):
        self.x = 0
        self.y = 0
        self.velocity = Vector()
        if sprite is not None:
            self.rect = sprite.get_rect()
        else:
            self.rect = pygame.Rect(0,0,1,1)
        self.sprite = sprite

    def update(self,dt):
        frameVel = self.velocity*(30*dt/1000)
        self.x += frameVel.x
        self.y += frameVel.y
        self.rect.x,self.rect.y = (self.x,self.y)

    def move(self,x,y):
        self.x = x
        self.y = y
        self.rect.x,self.rect.y = (x,y)

    def getPosition(self):
        return Vector(self.x,self.y)

class Room:
    def __init__(self,level):
        self.xsize = random.randint(4,10)
        self.ysize = random.randint(4,10)
        self.x = random.randint(0,level.xsize-self.xsize)
        self.y = random.randint(0,level.ysize-self.ysize)
        self.rect = pygame.Rect(self.x,self.y,self.xsize,self.ysize)

    def randomizePos(self,level):
        self.x = random.randint(0,level.xsize-self.xsize)
        self.y = random.randint(0,level.ysize-self.ysize)
        self.rect = pygame.Rect(self.x,self.y,self.xsize,self.ysize)

class Map:
    EMPTY = 0
    FLOOR = 1
    WALL = 2

    tilesize = 16 #tile size in pixels
    def __init__(self):
        self.xsize = 80
        self.ysize = 80

        self.numRooms = random.randint(6,12)
        self.rooms = []
        self.data = []

        #create columns
        for x in range(self.xsize):
            self.data.append([Map.EMPTY for y in range(self.ysize)])

        for i in range(self.numRooms):
            newRoom = Room(self)
            self.rooms.append(newRoom)

        for i in range(self.numRooms):
            room = self.rooms[i]
            if room.rect.collidelist([r.rect for r in self.rooms if r is not room]) != -1:
                room.randomizePos(self)
                i -= 1

        for room in self.rooms:
            for x in range(room.xsize):
                for y in range(room.ysize):
                    self.data[x+room.x][y+room.y] = Map.FLOOR

        for y in range(self.ysize):
            for x in range(self.xsize):
                tile = self.data[x][y]
                #print tile,
                if tile == Map.FLOOR:
                    sys.stdout.write('A')
                if tile == Map.EMPTY:
                    sys.stdout.write('-')
            sys.stdout.write('\n')

class Application:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(44100)

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.bg_colour = 0,0,0

        #Entity representing the mouse, no model
        self.mouseEntity = Entity(None)
        self.mouseEntity.move(*pygame.mouse.get_pos())

        self.score = 0
        self.lives = 3
        self.state = 0

        self.cameraX = 0
        self.cameraY = 0

        self.level = Map()
        self.floorTile = pygame.Surface((Map.tilesize,Map.tilesize))
        self.floorTile.fill((255,0,0))

        self.font = pygame.font.Font("PressStart2P.ttf",24)
#        self.dieSound = pygame.mixer.Sound("159408__noirenex__life-lost-game-over.wav")
#        self.endgameSound = pygame.mixer.Sound("171672__fins__failure-2.wav")

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.cameraY -= 5
                    elif event.key == pygame.K_s:
                        self.cameraY += 5
                    elif event.key == pygame.K_d:
                        self.cameraX += 5
                    elif event.key == pygame.K_a:
                        self.cameraX -= 5

            #Normal gameplay state
            if self.state == 0:
                dt = clock.tick(30) #Limit to 30 FPS
                
                self.mouseEntity.move(*pygame.mouse.get_pos())                
                self.draw()

    def draw(self):
        self.screen.fill(self.bg_colour)
        for x,column in enumerate(self.level.data):
            for y,tile in enumerate(self.level.data[x]):
                tilesize = Map.tilesize
                tilex = x*tilesize - self.cameraX*tilesize
                tiley = y*tilesize - self.cameraY*tilesize
                tilerect = pygame.Rect(tilex,tiley,tilesize,tilesize)
                if tile == Map.FLOOR:
                    self.screen.blit(self.floorTile,tilerect)
 
        pygame.display.flip()
Application().run()
pygame.quit()
sys.exit()
