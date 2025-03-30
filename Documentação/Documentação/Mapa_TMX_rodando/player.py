import pygame as pg

from settings import *


class Dash:
    def __init__(self, player):
        self.player = player
        self.dashing = False
        self.dash_pressed = False
        
        self.dash_speed = 10
        
        self.dash_timer = 0
        self.dash_duration = 10
        
        self.dash_cooldown_timer = 0
        self.dash_cooldown = 60
        self.dash_direction = pg.Vector2(0, 0)
        
    def start_dash(self, direction, last_direction):
        if self.dash_cooldown_timer == 0 and not self.dashing:
            self.dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            
            # Se a direção for zero, mantém a última direção válida
            if direction.length_squared() > 0:
                self.dash_direction = direction.normalize()
            else:
                self.dash_direction = last_direction.normalize()
    
    def update(self):
        if self.dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1


class Player(pg.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        original_image = pg.image.load('graphics/player.png').convert_alpha()
        
        self.image = pg.transform.scale(original_image, (original_image.get_width()//2, original_image.get_height()//2))
        self.rect = self.image.get_rect(center=pos)
        
        self.direction = pg.math.Vector2(0,1)
        self.last_direction = pg.math.Vector2(1, 0)  # Inicializa com uma direção padrão
        self.speed = 3.5
        self.dash = Dash(self)
        self.health = 100
        self.shield = 100

    def movimentacao(self):
        keys = pg.key.get_pressed()
        self.direction = pg.Vector2(0, 0)

        if keys[pg.K_UP] or keys[pg.K_w]:
            self.direction.y -= 1
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.direction.y += 1

        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.direction.x += 1
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.direction.x -= 1
        
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()
            self.last_direction = self.direction.copy()  # Atualiza a última direção válida
        
        if keys[pg.K_q]:
            self.dash.start_dash(self.direction, self.last_direction)

    def update(self):
        self.dash.update()
        self.movimentacao()
        
        if self.dash.dashing:
            self.rect.topleft += self.dash.dash_direction * self.dash.dash_speed
        else:
            self.rect.topleft += self.direction * self.speed

    def draw_health_bar(self, screen, cores):
        # Barra de Escudo
        pg.draw.rect(screen, cores['cinza'], (20, 20, 200, 20))  # Fundo
        pg.draw.rect(screen, cores['azul'], (20, 20, max(0, self.shield * 2), 20))  # Escudo

        # Barra de Vida
        pg.draw.rect(screen, cores['cinza'], (20, 50, 200, 20))  # Fundo
        pg.draw.rect(screen, cores['vermelho'], (20, 50, max(0, self.health * 2), 20))  # Vida

    def take_damage(self, amount):
        self.shield -= amount

        if self.shield < 0:
            self.shield = 0
            self.health -= amount

        if self.health < 0:
            self.health = 0
