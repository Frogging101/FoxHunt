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

class Turret(Entity):
    sprite = pygame.image.load("turret.png")
    def __init__(self):
        self.shootTimer = 0
        self.shootTimerEnd = random.randint(900,1500)
        super(Turret,self).__init__(Turret.sprite)
    
    def canSeePlayer(self,app):
        center = (self.x+self.rect.width//2,self.y+self.rect.height//2)
        toPlayer = Vector(app.player.x+app.player.rect.width//2,
                          app.player.y+app.player.rect.height//2)-\
                          Vector(*center)
        if toPlayer.getMagnitude() >= 14*Map.tilesize: #Player more than 14 tiles away
            return False
        toPlayer = toPlayer.normalize()

        rayLength = 24
        while rayLength < 14*Map.tilesize:
            ray = rayLength*toPlayer
            colliderRect = pygame.Rect(ray.x+center[0],ray.y+center[1],1,1)
            #If the ray hits anything that isn't this turret
            if colliderRect.collidelist([tile for tile in 
                                         app.level.collisionTiles 
                                         if tile != self.rect]) != -1:
                return False
            if colliderRect.colliderect(app.player.rect):
                return True
            rayLength += 24
        return True

    def update(self,dt,app):
        self.shootTimer += dt
        if self.shootTimer >= self.shootTimerEnd:
            if self.canSeePlayer(app):
                self.shoot(app)
            self.shootTimer = 0
            self.shootTimerEnd = random.randint(900,1500)

    def shoot(self,app):
        toPlayer = Vector(app.player.x+app.player.rect.width//2,
                          app.player.y+app.player.rect.height//2)-\
                          Vector(self.x+self.rect.width//2,self.y+self.rect.height//2)
        newBullet = Bullet((self.x+self.rect.width//2,self.y+self.rect.height//2),
                           toPlayer.normalize())
        app.bulletSound.play()
        app.bullets.append(newBullet)

class Bullet(Entity):
    sprite = pygame.image.load("bullet.png")
    def __init__(self,origin,direction):
        left = Vector(-1,0)
        angle = math.acos(Vector.dot(left,direction))*(180/math.pi)
        if direction.y < 0:
            angle = -angle
        self.sprite = pygame.transform.rotate(Bullet.sprite,angle)
        self.velocity = 25*direction
        self.x = origin[0]
        self.y = origin[1]
        self.rect = self.sprite.get_rect()

    def update(self,dt,app):
        if self.rect.collidelist(app.level.wallTiles) != -1:
            app.bullets.remove(self)
        elif self.rect.colliderect(app.player.rect):
            app.damageSound.play()
            app.bullets.remove(self)
        else:
            super(Bullet,self).update(dt)

class Room:
    def __init__(self,level):
        self.xSize = random.randint(4,10)
        self.ySize = random.randint(4,10)
        self.randomizePos(level)

    def randomizePos(self,level):
        self.x = random.randint(1,level.xSize-self.xSize-1)
        self.y = random.randint(1,level.ySize-self.ySize-1)
        self.rect = pygame.Rect(self.x,self.y,self.xSize,self.ySize)

class Map:
    EMPTY = 0
    FLOOR = 1
    WALL = 2
    TURRET = 3

    tilesize = 48 #tile size in pixels
    def __init__(self):
        self.xSize = 80
        self.ySize = 80

        self.numRooms = random.randint(6,12)
        self.rooms = []
        self.data = []
        self.collisionTiles = []
        self.wallTiles = []
        self.turrets = []

        #Initialize list of lists data[row][column]
        for x in range(self.xSize):
            self.data.append([Map.EMPTY for y in range(self.ySize)])

        for i in range(self.numRooms):
            newRoom = Room(self)
            self.rooms.append(newRoom)

        for i in range(self.numRooms):
            room = self.rooms[i]
            if room.rect.collidelist([r.rect for r in self.rooms if r is not room]) != -1:
                room.randomizePos(self)
                i -= 1

        #Create rooms
        for room in self.rooms:
            for x in range(room.xSize):
                for y in range(room.ySize):
                    self.data[x+room.x][y+room.y] = Map.FLOOR

        spawnRoom = self.rooms[random.randint(0,self.numRooms-1)]
        self.spawnX = spawnRoom.x*self.tilesize + (spawnRoom.xSize*self.tilesize)//2
        self.spawnY = spawnRoom.y*self.tilesize + (spawnRoom.ySize*self.tilesize)//2

        foxRoom = spawnRoom
        while foxRoom == spawnRoom:
            foxRoom = self.rooms[random.randint(0,self.numRooms-1)]
        self.foxX = foxRoom.x*self.tilesize + (foxRoom.xSize*self.tilesize)//2
        self.foxY = foxRoom.y*self.tilesize + (foxRoom.ySize*self.tilesize)//2

        #Create hallways between rooms
        for i in range(self.numRooms-1):
            room1 = self.rooms[i]
            room2 = self.rooms[i+1]
            
            xCenter1 = room1.x+room1.xSize//2
            xCenter2 = room2.x+room2.xSize//2
            yCenter1 = room1.y+room1.ySize//2
            yCenter2 = room2.y+room2.ySize//2
            
            if abs(xCenter1-xCenter2) > room1.xSize:
                if (xCenter1-xCenter2) < 0: #second room is to the right
                    hallwayStart = (room1.x+room1.xSize,yCenter1)
                else:
                    hallwayStart = (room1.x-1,yCenter1)
            else:
                if (yCenter1-yCenter2) < 0: #second room is higher
                    hallwayStart = (xCenter1,room1.y-1)
                else:
                    hallwayStart = (xCenter1,room1.y+room1.ySize)
            
            endX = hallwayStart[0]
            
            for x in range(abs(hallwayStart[0]-xCenter2)):
                if hallwayStart[0] < xCenter2:
                    self.data[hallwayStart[0]+x][yCenter1] = Map.FLOOR
                    endX += 1
                else:
                    self.data[hallwayStart[0]-x][yCenter1] = Map.FLOOR
                    endX -= 1

            for y in range(abs(hallwayStart[1]-yCenter2)):
                if hallwayStart[1] < yCenter2:
                    self.data[endX][hallwayStart[1]+y] = Map.FLOOR
                else:
                    self.data[endX][hallwayStart[1]-y] = Map.FLOOR
            
        #Yet another loop through the rooms. This time we're
        #adding turrets
        for room in self.rooms:
            if room == spawnRoom:
                continue
            for tile in range(room.xSize*room.ySize):
                if random.random() < 1/10:
                    tileX = room.x+tile%room.xSize
                    tileY = room.y+tile//room.xSize
                    self.data[tileX][tileY] = Map.TURRET
                    newTile = pygame.Rect(tileX*self.tilesize,tileY*self.tilesize,
                                          self.tilesize,self.tilesize)
                    self.collisionTiles.append(newTile)
                    newTurret = Turret()
                    newTurret.move(tileX*Map.tilesize,tileY*Map.tilesize)
                    self.turrets.append(newTurret)

        #Finally add the walls
        for y in range(1,self.ySize-1):
            for x in range(1,self.xSize-1):
                if self.data[x][y] != Map.EMPTY and self.data[x][y] != Map.WALL:
                    adjacents = []
                    adjacents.append((x-1,y-1))
                    adjacents.append((x-1,y+1))
                    adjacents.append((x-1,y))
                    adjacents.append((x,y-1))
                    adjacents.append((x,y+1))
                    adjacents.append((x+1,y+1))
                    adjacents.append((x+1,y-1))
                    adjacents.append((x+1,y))
                    for pos in adjacents:
                        if self.data[pos[0]][pos[1]] == Map.EMPTY:
                            self.data[pos[0]][pos[1]] = Map.WALL
                            newTile = pygame.Rect(pos[0]*self.tilesize,pos[1]*self.tilesize,self.tilesize,self.tilesize)
                            self.collisionTiles.append(newTile)
                            self.wallTiles.append(newTile)
                x += 1
            y += 1

        for y in range(self.ySize):
            for x in range(self.xSize):
                tile = self.data[x][y]
                #print tile,
                if tile == Map.FLOOR:
                    sys.stdout.write('A')
                elif tile == Map.EMPTY:
                    sys.stdout.write('-')
                else:
                    sys.stdout.write(str(tile))
            sys.stdout.write('\n')

class Application:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(44100)

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width,self.height))
        Bullet.sprite = Bullet.sprite.convert_alpha() #This is here because it has to be done after init
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
        self.floorTile = pygame.image.load("floor.png")
        self.turretTile = pygame.image.load("turret.png")
        self.wallTile = pygame.image.load("wall.png")
        self.player = Entity(pygame.image.load("player.png"))
        self.player.move(self.level.spawnX,self.level.spawnY)
        self.fox = Entity(pygame.image.load("fox.png"))
        self.fox.move(self.level.foxX,self.level.foxY)

        self.bulletSound = pygame.mixer.Sound("bullet.wav")
        self.bgm = pygame.mixer.music.load("bg.wav")
        self.damageSound = pygame.mixer.Sound("oof.wav")

        self.bullets = []

        self.font = pygame.font.Font("PressStart2P.ttf",24)
        pygame.mixer.music.play()

    def collideLevel(self,obj,direction):
        return
        obj = pygame.Rect(obj)
        collideX = False
        collideY = False

        obj.x += 11*direction.x
        if obj.collidelist(self.level.collisionTiles) != -1:
            collideX = True
        obj.x -= 11*direction.x
        obj.y += 11*direction.y
        if obj.collidelist(self.level.collisionTiles) != -1:
            collideY = True

        if collideX:
            direction.x = 0
        if collideY:
            direction.y = 0

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            #Normal gameplay state
            if self.state == 0:
                dt = clock.tick(30) #Limit to 30 FPS

                keys = pygame.key.get_pressed()
                direction = Vector()
                if keys[pygame.K_w]:
                    direction += Vector(0,-1)
                if keys[pygame.K_s]:
                    direction += Vector(0,1)
                if keys[pygame.K_a]:
                    direction += Vector(-1,0)
                if keys[pygame.K_d]:
                    direction += Vector(1,0)

                self.collideLevel(self.player.rect,direction)
                self.player.x += 11*direction.x#*30*dt/1000
                self.player.y += 11*direction.y#*30*dt/1000

                self.player.update(dt)
                for turret in self.level.turrets:
                    turret.update(dt,self)
                for bullet in self.bullets:
                    bullet.update(dt,self)

                self.cameraX = self.player.x+self.player.rect.width//2-self.width//2
                self.cameraY = self.player.y+self.player.rect.height//2-self.height//2

                self.mouseEntity.move(*pygame.mouse.get_pos())
                self.draw()

    def draw(self):
        self.screen.fill(self.bg_colour)
        for x,column in enumerate(self.level.data):
            for y,tile in enumerate(self.level.data[x]):
                tilesize = Map.tilesize
                tilex = x*tilesize - self.cameraX
                tiley = y*tilesize - self.cameraY
                tilerect = pygame.Rect(tilex,tiley,tilesize,tilesize)
                if tile == Map.FLOOR:
                    self.screen.blit(self.floorTile,tilerect)
                if tile == Map.TURRET:
                    self.screen.blit(self.floorTile,tilerect)
                    self.screen.blit(self.turretTile,tilerect)
                if tile == Map.WALL:
                    self.screen.blit(self.wallTile,tilerect)
        playerScreenRect = self.player.rect.move(-self.cameraX,-self.cameraY)
        self.screen.blit(self.player.sprite,playerScreenRect)
        for bullet in self.bullets:
            bulletScreenRect = bullet.rect.move(-self.cameraX,-self.cameraY)
            self.screen.blit(bullet.sprite,bulletScreenRect)
        foxScreenRect = self.fox.rect.move(-self.cameraX,-self.cameraY)
        self.screen.blit(self.fox.sprite,foxScreenRect)

        pygame.display.flip()
Application().run()
pygame.quit()
sys.exit()
