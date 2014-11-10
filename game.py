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
        #Timer, turret will fire when it reaches a certain random number
        self.shootTimer = 0
        self.shootTimerEnd = random.randint(900,1325)
        self.health = random.randint(2,3)*50
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
                                         app.level.wallTiles]) != -1:
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
        if self.health <= 0:
            app.level.turrets.remove(self)
            app.score += 100

    def shoot(self,app):
        #all this arithmetic is to make a vector from the center of
        #the turret to the center of the player
        toPlayer = Vector(app.player.x+app.player.rect.width//2,
                          app.player.y+app.player.rect.height//2)-\
                          Vector(self.x+self.rect.width//2,self.y+self.rect.height//2)
        newBullet = Bullet((self.x+self.rect.width//2,self.y+self.rect.height//2),
                           toPlayer.normalize())
        app.bulletSound.play()
        app.bullets.append(newBullet)

class Bullet(Entity):
    sprite = pygame.image.load("bullet.png")
    def __init__(self,origin,direction,playerFired=False):
        self.playerFired = playerFired
        left = Vector(-1,0)
        #Angle to rotate bullet sprite
        angle = math.acos(Vector.dot(left,direction))*(180/math.pi)
        if direction.y < 0:
            angle = -angle
        self.sprite = pygame.transform.rotate(Bullet.sprite,angle)
        self.velocity = 22*direction
        self.x = origin[0]
        self.y = origin[1]
        self.rect = self.sprite.get_rect()

    def update(self,dt,app):
        if self.rect.collidelist(app.level.wallTiles) != -1:
            app.bullets.remove(self)
        elif self.rect.colliderect(app.player.rect) and not self.playerFired:
            app.damageSound.play()
            app.health -= random.randint(7,15)
            app.bullets.remove(self)
        elif self.playerFired:
            turretHit = self.rect.collidelist([turret.rect for turret in app.level.turrets])
            if turretHit != -1: #if a turret was hit
                app.bullets.remove(self)
                app.level.turrets[turretHit].health -= 50
                
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
    #Tile types
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
                if random.random() < 1/15:
                    tileX = room.x+tile%room.xSize
                    tileY = room.y+tile//room.xSize
                    self.data[tileX][tileY] = Map.TURRET
                    newTile = pygame.Rect(tileX*self.tilesize,tileY*self.tilesize,
                                          self.tilesize,self.tilesize)
                    newTurret = Turret()
                    newTurret.move(tileX*Map.tilesize,tileY*Map.tilesize)
                    self.turrets.append(newTurret)

        #Finally add the walls
        for y in range(1,self.ySize-1):
            for x in range(1,self.xSize-1):
                if self.data[x][y] != Map.EMPTY and self.data[x][y] != Map.WALL:
                    adjacents = []
                    #Positions of all the adjacent tiles, so they may be looped through
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
        pygame.display.set_caption("FoxHunt v0.1")
        Bullet.sprite = Bullet.sprite.convert_alpha() #This is here because it has to be done after init
        self.bg_colour = 0,0,0

        #Entity representing the mouse, no model
        self.mouseEntity = Entity(None)
        self.mouseEntity.move(*pygame.mouse.get_pos())
        #Tiles
        self.floorTile = pygame.image.load("floor.png")
        self.turretTile = pygame.image.load("turret.png")
        self.wallTile = pygame.image.load("wall.png")

        #Entities
        self.player = Entity(pygame.image.load("player.png"))
        self.fox = Entity(pygame.image.load("fox.png"))

        #Sounds
        self.bulletSound = pygame.mixer.Sound("bullet.wav")
        self.bgm = pygame.mixer.music.load("bg.wav")
        self.damageSound = pygame.mixer.Sound("oof.wav")
        self.pickupSound = pygame.mixer.Sound("pickup.wav")
        self.winSound = pygame.mixer.Sound("eb-youwin.wav")
        self.gameOverSound = pygame.mixer.Sound("eb-loss.wav")
        self.dieSound = pygame.mixer.Sound("159408__noirenex__life-lost-game-over.wav")
        
        self.foximg = pygame.image.load("foxhunt_f.png")
        self.font = pygame.font.Font("PressStart2P.ttf",24)
        self.state = 2

    def gameInit(self):
        self.score = 0
        self.lives = 3
        self.state = 0
        self.win = False
        self.health = 100

        self.cameraX = 0
        self.cameraY = 0
        
        self.level = Map()
        self.player.move(self.level.spawnX,self.level.spawnY)
        self.fox.move(self.level.foxX,self.level.foxY)
        self.bullets = []
        
    def collideLevel(self,obj,direction):
        obj = pygame.Rect(obj)
        collideX = False
        collideY = False

        obj.x += 11*direction.x
        #If it collided with a wall or a turret while moving on the X axis
        if obj.collidelist(self.level.wallTiles) != -1 or\
           obj.collidelist([turret.rect for turret in self.level.turrets]) != -1:
            collideX = True
        obj.x -= 11*direction.x
        obj.y += 11*direction.y
        #do this again but in the Y direction
        if obj.collidelist(self.level.wallTiles) != -1 or\
           obj.collidelist([turret.rect for turret in self.level.turrets]) != -1:
            collideY = True

        #kill movement if it would have hit a wall
        if collideX:
            direction.x = 0
        if collideY:
            direction.y = 0

    def signalBar(self):
        distance = (Vector(self.player.x,self.player.y)-\
                    Vector(self.fox.x,self.fox.y)).getMagnitude()
        strength = min(12000.0/distance**2,1.0)
        width = (400*strength)
        bar = pygame.Surface((width,30))
        bar.fill((0,255,0))
        bar.set_alpha(0.75*255)
        return bar

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            #Normal gameplay state
            if self.state == 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        origin = (self.player.x+self.player.rect.width//2,
                                  self.player.y+self.player.rect.height//2)
                        mousePos = pygame.mouse.get_pos()
                        mouseX = mousePos[0]+self.cameraX
                        mouseY = mousePos[1]+self.cameraY
                        direction = (Vector(mouseX,mouseY)-\
                                    Vector(origin[0],origin[1])).normalize()
                        newBullet = Bullet(origin,direction,True)
                        self.bulletSound.play()
                        self.bullets.append(newBullet)
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
                
                if self.player.rect.colliderect(self.fox.rect):
                    self.pickupSound.play()
                    self.win = True
                    self.state = 1
                    self.score += 1250

                if self.lives < 0:
                    self.state = 1

                if self.health < 0:
                    self.dieSound.play()
                    pygame.time.delay(int(self.dieSound.get_length()*1000))
                    self.player.move(self.level.spawnX,self.level.spawnY)
                    self.lives -= 1      
                    self.health = 100              

                self.cameraX = self.player.x+self.player.rect.width//2-self.width//2
                self.cameraY = self.player.y+self.player.rect.height//2-self.height//2

                self.mouseEntity.move(*pygame.mouse.get_pos())
                self.draw()

            elif self.state == 1:
                pygame.mixer.music.stop()
                if self.win:
                    sound = self.winSound
                else:
                    sound = self.gameOverSound
                timer = 0
                played = False
                endgame = True
                fadeSurface = pygame.Surface((self.width,self.height))
                fadeSurface.fill((0,0,0))
                fadeSurface.set_alpha(0)
                while endgame:
                    if timer > 1000 and not played:
                        played = True
                        sound.play()
                    dt = clock.tick(30)
                    timer += dt
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            endgame = False
                        if event.type == pygame.MOUSEBUTTONDOWN and timer > 2000:
                            endgame = False
                    fadeout = 5000
                    fadeSurface.set_alpha(min(int((timer)*(255/fadeout)),255))
                    self.screen.blit(fadeSurface,fadeSurface.get_rect())
                    if timer > fadeout/3:
                        if not self.win:
                            GOtext = self.font.render("Game Over",True,(255,255,255))
                        else:
                            GOtext = self.font.render("Fox get! You win!",True,(255,255,255))
                            foximgRect = self.foximg.get_rect()
                            foximgRect = foximgRect.move(self.width//2-foximgRect.width//2,self.height//3+10)
                            self.screen.blit(self.foximg,foximgRect)
                        clickText = self.font.render("Click to return to start screen",True,(255,255,255))

                        goTextRect = GOtext.get_rect()
                        clickTextRect = clickText.get_rect()
                        clickTextRect = clickTextRect.move(self.width/2.0-clickTextRect.width/2.0,
                                                           self.height/4.0-clickTextRect.height/2.0+\
                                                           goTextRect.height)
                        goTextRect = goTextRect.move(self.width/2.0-goTextRect.width/2.0,
                                                     self.height/4.0-goTextRect.height/2.0-\
                                                     clickTextRect.height)
                        scoreText = self.font.render("Score: "+str(self.score),True,(255,255,255))
                        scoreTextRect = scoreText.get_rect()
                        scoreTextRect = scoreTextRect.move(self.width-scoreTextRect.width,0)

                        self.screen.blit(scoreText,scoreTextRect)
                        self.screen.blit(GOtext,goTextRect)
                        self.screen.blit(clickText,clickTextRect)
                    pygame.display.flip()
                sound.stop()
                self.state = 2
            
            elif self.state == 2:
                pygame.mixer.music.stop()
                self.screen.fill((0,0,0))
                menu = True
                while menu:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            menu = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            menu = False
                    playText = self.font.render("Click to play",True,(255,255,255))
                    playTextRect = playText.get_rect()
                    playTextRect = playTextRect.move(self.width//2-playTextRect.width//2,
                                                     self.height//3)
                    
                    sysfont = pygame.font.SysFont("monospace",24)
                    attribText = sysfont.render("John Brooks | http://www.fastquake.com/",True,(255,255,255))
                    attribTextRect = attribText.get_rect()
                    attribTextRect = attribTextRect.move(self.width//2-attribTextRect.width//2,
                                                         self.height-attribTextRect.height)
                    
                    self.screen.blit(attribText,attribTextRect)
                    self.screen.blit(playText,playTextRect)
                    
                    pygame.display.flip()
                pygame.mixer.music.rewind()
                pygame.mixer.music.play(-1) #Play looping music
                self.gameInit() #Initialize game world

    def draw(self):
        self.screen.fill(self.bg_colour)
        for x,column in enumerate(self.level.data):
            for y,tile in enumerate(self.level.data[x]):
                tilesize = Map.tilesize
                tilex = x*tilesize - self.cameraX
                tiley = y*tilesize - self.cameraY
                tilerect = pygame.Rect(tilex,tiley,tilesize,tilesize)
                if tile == Map.FLOOR or tile == Map.TURRET:
                    self.screen.blit(self.floorTile,tilerect)
                if tile == Map.WALL:
                    self.screen.blit(self.wallTile,tilerect)
        playerScreenRect = self.player.rect.move(-self.cameraX,-self.cameraY)
        self.screen.blit(self.player.sprite,playerScreenRect)
        for bullet in self.bullets:
            bulletScreenRect = bullet.rect.move(-self.cameraX,-self.cameraY)
            self.screen.blit(bullet.sprite,bulletScreenRect)
        for turret in self.level.turrets:
            turretScreenRect = turret.rect.move(-self.cameraX,-self.cameraY)
            self.screen.blit(self.turretTile,turretScreenRect)
        foxScreenRect = self.fox.rect.move(-self.cameraX,-self.cameraY)
        self.screen.blit(self.fox.sprite,foxScreenRect)

        livesText = self.font.render("Lives: "+str(self.lives),True,(255,255,255))
        livesTextRect = livesText.get_rect()
        healthText = self.font.render("Health: "+str(self.health),True,(255,255,255))
        healthTextRect = healthText.get_rect()
        healthTextRect = healthTextRect.move(0,livesTextRect.height)

        scoreText = self.font.render("Score: "+str(self.score),True,(255,255,255))
        scoreTextRect = scoreText.get_rect()
        scoreTextRect = scoreTextRect.move(self.width-scoreTextRect.width,0)

        self.screen.blit(scoreText,scoreTextRect)
        self.screen.blit(livesText,livesTextRect)
        self.screen.blit(healthText,healthTextRect)

        signalText = self.font.render("Signal",True,(255,255,255))
        signalTextRect = signalText.get_rect()
        signalTextRect = signalTextRect.move(self.width//2-\
                                             signalTextRect.width//2,0)

        bar = self.signalBar()
        barRect = bar.get_rect()
        barRect = barRect.move(self.width//2-barRect.width//2,
                               signalTextRect.height+5)

        self.screen.blit(signalText,signalTextRect)
        self.screen.blit(bar,barRect)

        pygame.display.flip()
Application().run()
pygame.quit()
sys.exit()
