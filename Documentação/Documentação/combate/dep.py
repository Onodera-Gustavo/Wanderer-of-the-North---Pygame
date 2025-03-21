import pygame as pg
import math

from settings import *

pg.init()

# Configurações da tela
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

# Cores
# cores['branco'] = (255, 255, 255)
# cores['vermelho'] = (255, 0, 0)
# cores['verde'] = (0, 255, 0)
# cores['azul'] = (0, 0, 255)

# Classe do Jogador
class Player:
    def __init__(self, x, y):
        self.image = pg.Surface((40, 40))
        self.image.fill(cores['vermelho'])
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = 1
        self.speed = 5
        self.dash_speed = 15
        self.dashing = False
        self.dash_timer = 0
        self.dash_duration = 10
        self.dash_cooldown = 30
        self.dash_cooldown_timer = 0
        self.dash_pressed = False

    def move(self, keys):
        if self.dashing:
            self.rect.x += self.direction * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
                self.dash_cooldown_timer = self.dash_cooldown

        else:
            if keys[pg.K_a]:
                self.rect.x -= self.speed
                self.direction = -1
            if keys[pg.K_d]:
                self.rect.x += self.speed
                self.direction = 1
            if keys[pg.K_w]:
                self.rect.y -= self.speed
            if keys[pg.K_s]:
                self.rect.y += self.speed

            if keys[pg.K_q] and not self.dashing and self.dash_cooldown_timer <= 0 and not self.dash_pressed:
                self.dashing = True
                self.dash_timer = self.dash_duration
                self.dash_pressed = True

        if not keys[pg.K_q]:
            self.dash_pressed = False

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Classe da Espada
class Sword:
    def __init__(self, player):
        self.radius = 50
        self.angle = 0
        self.attack_rotation = 0
        self.attacking = False
        self.player = player
        self.hit_enemy = False  # Flag para impedir múltiplos hits no mesmo ataque
        
    def update(self):
        if self.attacking:
            self.attack_rotation += 20 * self.player.direction
            if abs(self.attack_rotation) >= 180:
                self.attack_rotation = 0
                self.attacking = False
                self.hit_enemy = False  # Reseta a flag para o próximo ataque
        else:
            self.angle = -50 if self.player.direction == 1 else 230
    
    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.attack_rotation = 0
            self.hit_enemy = False  # Permite que o próximo ataque cause dano
    
    def get_positions(self):
        """ Retorna as coordenadas do cabo e da ponta da espada """
        angle_rad = math.radians(self.angle + self.attack_rotation)
        sword_tip_x = self.player.rect.centerx + self.radius * math.cos(angle_rad)
        sword_tip_y = self.player.rect.centery + self.radius * math.sin(angle_rad)
        return (self.player.rect.centerx, self.player.rect.centery), (sword_tip_x, sword_tip_y)

    def check_collision(self, enemy):
        """ Verifica se qualquer parte da espada atinge o inimigo """
        if self.hit_enemy:  # Se já acertou, não pode causar outro hit
            return False

        (x1, y1), (x2, y2) = self.get_positions()
        
        for i in range(0, 101):  # Divide a linha em 100 pontos
            px = x1 + (x2 - x1) * i / 100
            py = y1 + (y2 - y1) * i / 100
            if enemy.rect.collidepoint(px, py):  # Se acertar, marca que já houve hit
                self.hit_enemy = True
                return True
        return False
    
    def draw(self, surface):
        pg.draw.line(surface, cores['branco'], *self.get_positions(), 5)

# Classe da Barra de Vida
class HealthBar:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.max_hp = max_hp
        self.hp = max_hp
    
    def update(self, current_hp):
        self.hp = current_hp
    
    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pg.draw.rect(surface, cores['vermelho'], (self.x, self.y, self.w, self.h))
        pg.draw.rect(surface, cores['verde'], (self.x, self.y, self.w * ratio, self.h))

# Classe do Inimigo
class Enemy:
    def __init__(self, x, y, health):
        self.image = pg.Surface((40, 40))
        self.image.fill(cores['verde'])
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health
        self.max_health = health
        self.health_bar = HealthBar(self.rect.centerx - 25, self.rect.top - 10, 50, 5, health)  
    
    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        self.health_bar.update(self.health)
        print(f"Inimigo recebeu {damage} de dano! Vida restante: {self.health}")

    def is_dead(self):
        return self.health <= 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.health_bar.x = self.rect.centerx - 25
        self.health_bar.y = self.rect.top - 10
        self.health_bar.draw(surface)

# Classe do Arqueiro (ArcherSkeleton)
class ArcherSkeleton:
    def __init__(self, x, y):
        self.image = pg.Surface((40, 40))
        self.image.fill(cores['azul'])
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 80
        self.attack_cooldown = 40  # Tempo entre tiros
        self.cooldown_timer = 0
    
    def update(self, projectiles, player):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        else:
            self.shoot(projectiles, player)
            self.cooldown_timer = self.attack_cooldown

    def shoot(self, projectiles, player):
        direction = pg.Vector2(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        if direction.length() > 0:
            direction.normalize_ip()
        projectiles.append(Projectile(self.rect.centerx, self.rect.centery, direction))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Classe dos Projetéis
class Projectile:
    def __init__(self, x, y, direction):
        self.image = pg.Surface((10, 10))
        self.image.fill(cores['branco'])
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 5

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Inicialização
player = Player(WIDTH // 2, HEIGHT // 2)
sword = Sword(player)
enemy = Enemy(WIDTH // 3, HEIGHT // 2, 100)
archer = ArcherSkeleton(WIDTH // 2, HEIGHT // 3)
projectiles = []

running = True
while running:
    screen.fill((0, 0, 0))
    keys = pg.key.get_pressed()
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            sword.attack()
    
    player.move(keys)
    sword.update()
    archer.update(projectiles, player)

    # Colisão da espada com o inimigo
    if enemy:
        if sword.attacking and sword.check_collision(enemy):  # Só dá dano uma vez por ataque
            enemy.take_damage(20)
            if enemy.is_dead():
                enemy = None  # Remove o inimigo se ele morrer

    # Atualizar e desenhar os projectéis
    for projectile in projectiles[:]:
        projectile.update()
        if not screen.get_rect().colliderect(projectile.rect):  # Remover projectéis fora da tela
            projectiles.remove(projectile)
    
    # Desenho
    player.draw(screen)
    sword.draw(screen)
    
    if enemy:
        enemy.draw(screen)

    archer.draw(screen)
    
    for projectile in projectiles:
        projectile.draw(screen)

    pg.display.flip()
    clock.tick(60)

pg.quit()