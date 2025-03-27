import pygame
import math


class Dash:
    def __init__(self, dash_speed=10, dash_time=10, cooldown=60):
        self.dash_speed = dash_speed
        self.dash_time = dash_time
        self.cooldown = cooldown
        self.dashing = False
        self.dash_timer = 0
        self.cooldown_timer = 0

    def start_dash(self):
        if self.cooldown_timer == 0 and not self.dashing:
            self.dashing = True
            self.dash_timer = self.dash_time
            self.cooldown_timer = self.cooldown

    def update(self):
        if self.dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False

        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1



class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        original_image = pygame.image.load('graphics/player.png').convert_alpha()
        
        self.image = pygame.transform.scale(original_image, (original_image.get_width()//4, original_image.get_height()//4))
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = 3.5
        self.dash = Dash()
        self.health = 100
        self.shield = 100

    def movimentacao(self):
        keys = pygame.key.get_pressed()
        vel = self.speed + (self.dash.dash_speed if self.dash.dashing else 0)

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        if keys[pygame.K_q]:
            self.dash.start_dash()

    def update(self):
        self.dash.update()
        self.movimentacao()
        vel = self.speed + (self.dash.dash_speed if self.dash.dashing else 0)
        self.rect.center += self.direction * vel

    def draw_health_bar(self):
        # Barra de Escudo
        pygame.draw.rect(screen, CINZA, (20, 20, 200, 20))  # Fundo
        pygame.draw.rect(screen, AZUL, (20, 20, max(0, self.shield * 2), 20))  # Escudo

        # Barra de Vida
        pygame.draw.rect(screen, CINZA, (20, 50, 200, 20))  # Fundo
        pygame.draw.rect(screen, VERMELHO, (20, 50, max(0, self.health * 2), 20))  # Vida

    def take_damage(self, amount):
        self.shield -= amount

        if self.shield < 0:
            self.shield = 0
            self.health -= amount

        if self.health < 0:
            self.health = 0

