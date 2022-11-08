import pygame, time
from toplefttext import debug
import random



class player(pygame.sprite.Sprite):
    def __init__(self,group,pos,renderbullet,surface,enemy):
        super().__init__(group)
        self.group = group
        self.enemysprites = enemy
        self.image = pygame.image.load('assets/wizard.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.direction = pygame.math.Vector2()
        self.movespd = 5
        self.facing = 'n'
        self.surface = surface

        self.renderbullet = renderbullet

        self.attacking = False
        self.attCooldown = 400
        self.attack_time = 0

        self.gamePaused = False
    
    def controller(self):
     keys = pygame.key.get_pressed()
     
     if keys[pygame.K_o]:
            if self.gamePaused:
                self.gamePaused = False
            else:
                self.gamePaused = True

     if not self.gamePaused:
        #print(f"{self.direction} : player direction")
        mouse = pygame.mouse.get_pressed()
        debug(f"{pygame.mouse.get_pos()}")
        debug(f"player pos : {self.rect.x},{self.rect.y}",y = 40)

        if keys[pygame.K_a]:
            self.direction.x = -1
            self.facing = 'w'
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.facing = 'e'
        else:
            self.direction.x = 0
        
        if keys[pygame.K_w]:
            self.direction.y = -1
            self.facing = 'n'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.facing = 's'
        else:
            self.direction.y = 0
            
#        if keys[pygame.K_SPACE]:
#            if not self.attacking:
#                self.attacking = True
#                self.attack_time = pygame.time.get_ticks()
#                self.renderbullet(self.rect.center,self.facing,self)
        
        if mouse[0]:
            if not self.attacking:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                mousepos = pygame.mouse.get_pos()
                deathbeam(pos = pygame.math.Vector2(mousepos[0] - (1280 // 2) + self.rect.centerx,mousepos[1] - (720//2) + self.rect.centery),group=self.group[0],direct=self.direction,plr=self)


    def cooldowns(self):
        if self.attacking:
            if ( pygame.time.get_ticks() - self.attack_time ) >= 450:
                self.attacking = False 
    
    def movement(self):
        self.rect.y += (self.direction.y * self.movespd)
        self.rect.x += (self.direction.x * self.movespd)

    def update(self):
        self.cooldowns()
        self.controller()
        self.movement()
        #debug(f'{self.rect.x},{self.rect.y}')

        if self.rect.y <= 0:
            self.rect.y = 0
        elif self.rect.y >= 720:
            self.rect.y = 720
        
        if self.rect.x <= 0 :
            self.rect.x = 0
        elif self.rect.x >= 1280:
            self.rect.x = 1280

class projectile(pygame.sprite.Sprite):
    def __init__(self,group,pos,direct,plr) -> None:
        super().__init__(group)
        self.image = pygame.image.load('assets/bullet.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.hitbox = self.rect.inflate(20,20)
        self.direction = direct

        self.time = pygame.time.get_ticks()
        self.lifespan = 300
        self.player = plr

        self.damage = 1
        
    def collideEnemyDetect(self):
        for sprite in self.player.enemysprites:
            if sprite.rect.colliderect(self.rect):
                sprite.health -= 1
                if sprite.health <= 0:
                    sprite.kill()
                    sprite.hpdisplay.kill()
    
    def killSelf(self):
        if (pygame.time.get_ticks() - self.time) >= self.lifespan:
            self.kill()

    def bulletTravel(self):
        if self.direction == 'n':
            self.rect.y -= 10
        elif self.direction == 's':
            self.rect.y+= 10
        elif self.direction == 'e':
            self.rect.x += 10
        elif self.direction == 'w':
            self.rect.x -= 10
        elif self.direction == 'n' and self.direction == 'e':
            self.rect.y -= 10
            self.rect.x += 10

class Ycamerasort(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2();
        self.half_width = self.surface.get_size()[0] 
        self.half_height = self.surface.get_size()[1] 
        
    def customDraw(self,player):

        # player cam offset
        self.offset.x = player.rect.centerx - self.half_width //2
        self.offset.y = player.rect.centery - self.half_height //2

        # magic to render which sprite should be on top
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery): 
            offset_pos = sprite.rect.topleft - self.offset
            if sprite.image:
                self.surface.blit(sprite.image, offset_pos)

class deathbeam(projectile):
    def __init__(self, pos,group,direct,plr) -> None:
        super().__init__(group=group,pos=pos,direct=direct,plr=plr)

        self.graphic = projectile(group=group,pos=pos,direct=direct,plr=plr)
        self.graphic.image = pygame.image.load('assets/beam.png').convert_alpha()
        self.graphic.rect = self.graphic.image.get_rect(center = self.rect.center); self.graphic.rect.y -= 50
        self.graphic.lifespan = self.lifespan
        
        self.image = pygame.image.load('assets/blankairstrike.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)

        self.time = pygame.time.get_ticks()
        self.lifespan = 300

    def destroySelf(self):
        if (pygame.time.get_ticks() - self.time) >= self.lifespan:
            self.kill()

    def update(self):
        self.collideEnemyDetect()
        self.destroySelf()
        self.graphic.killSelf()


class melee(projectile):
    def __init__(self,group,pos,direct,plr):
        super().__init__(group,pos,direct,plr)
        self.image = pygame.image.load('assets/hitbox.png').convert_alpha()

        if self.direction == 'e':
            self.rect = self.image.get_rect(midleft = self.player.rect.midright)
        if self.direction == 'w':
            self.rect = self.image.get_rect(midright = self.player.rect.midleft)
        if self.direction == 'n':
            self.rect = self.image.get_rect(midbottom = self.player.rect.midtop)
        if self.direction == 's':
            self.rect = self.image.get_rect(midtop = self.player.rect.midbottom)

    def update(self):
        #self.bulletTravel()
        self.killSelf()
        self.collideEnemyDetect()



class enitity(pygame.sprite.Sprite):
    def __init__(self,group,pos,player) -> None:
        super().__init__(group)
        self.image = pygame.image.load('assets/apple.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)  
        self.plr = player
        self.plrPOS = None
        self.health = 100
        self.hpdisplay = enemyhpdisplay([group[0]],self)

    def getplrpos(self):
        #will be put into the update method
        self.plrPOS = [self.plr.rect.x,self.plr.rect.y]

    def simplemovement(self):

     if not self.plr.gamePaused:
        if self.plrPOS[0] >= self.rect.x:
            self.rect.x += 2
        elif self.plrPOS[0] <= self.rect.x:
            self.rect.x -= 2
        
        if self.plrPOS[1] >= self.rect.y:
            self.rect.y += 2
        elif self.plrPOS[1] <= self.rect.y:
            self.rect.y -= 2

    def update(self):
        self.getplrpos()
        self.simplemovement()

class enemyhpdisplay(pygame.sprite.Sprite):
    def __init__(self,group,entity) -> None:
        super().__init__(group[0])
        self.parent = entity
        self.font = pygame.font.Font(None,30)
        self.image = self.font.render(f"{self.parent.health} / 100",True,'Black')
        self.rect = self.image.get_rect(bottom = entity.rect.top)
    
    def getposition(self,rect):
        self.rect.midbottom = rect.midtop
    
    def updateHealth(self):
        self.image = self.font.render(f"{self.parent.health} / 100",True,'Black')

    def update(self):
        self.getposition(self.parent.rect)
        self.updateHealth()

class tree(enitity):
    def __init__(self, group, pos, player) -> None:
        super().__init__(group, pos, player)
        self.surface = pygame.display.get_surface()
        self.image = pygame.image.load('assets/tree.png')
        self.rect = self.image.get_rect(topleft = pos)
        #self.hpdisplay.rect.x -= 10

        self.spawntime = 0

    
    def update(self):
        self.hpdisplay.getposition(self.rect)
        self.getplrpos()
        self.simplemovement()

class renderer:
    def __init__(self):
        self.surface = pygame.display.get_surface()
        self.visible_sprites = Ycamerasort()
        self.enemy_sprite = pygame.sprite.Group()
        self.plr = player([self.visible_sprites],(0,0),renderbullet=self.renderbullet,surface=self.surface,enemy=self.enemy_sprite)
        #self.testenemy = enitity([self.visible_sprites,self.enemy_sprite],(50,50),self.plr)
        self.tree = tree([self.visible_sprites,self.enemy_sprite],(250,250),self.plr)
        self.spawntime = 0
    
    def renderbullet(self,pos,direct,plr):
        melee([self.visible_sprites],pos,direct,plr)

    def spawnTrees(self):
     if not self.plr.gamePaused:
        cooldown = 3000

        if (pygame.time.get_ticks() - self.spawntime) >= cooldown:
            #spawntime = pygame.time.get_ticks()
            tree([self.visible_sprites,self.enemy_sprite],(random.randint(1,1280),random.randint(1,720)),self.plr)
            self.spawntime = pygame.time.get_ticks()
            print(f'spawned')

                
    def run(self):
        self.surface.blit(pygame.image.load('assets/grass.png'),dest=(0,0))
        self.visible_sprites.customDraw(self.plr)
        self.visible_sprites.update()
        self.spawnTrees()

clock = pygame.time.Clock()
class Game():
    def __init__(self) -> None:
        pygame.init()
        self.FPS = 75;
        self.WIN = pygame.display.set_mode((1280,720)) # test resolution will be changed later
        pygame.display.set_caption("wasd - to move, leftclick - to blast")
        self.renderer = renderer()

    def run(self):
        while True:
         clock.tick(self.FPS)
         self.renderer.run()
         debug(f"{clock.get_fps()}",y=70)
         for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0; 
            if event.type == pygame.QUIT:
                raise SystemExit
         pygame.display.update() 


if __name__ == "__main__":
    game = Game()
    game.run()