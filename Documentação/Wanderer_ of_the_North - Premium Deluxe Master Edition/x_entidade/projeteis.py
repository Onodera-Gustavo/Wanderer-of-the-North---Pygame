import pygame as pg
from settings import cores

import math
from settings import cores

class Projectile:
    def __init__(self, x, y, direction, speed, owner, damage=15, size=10, color=cores['azul']):
        self.image = pg.Surface((size, size))
        self.image.fill(color if color else cores['azul'])
        self.rect = self.image.get_rect(center=(x, y))
        
        self.direction = direction.normalize() if direction.length() > 0 else pg.math.Vector2(1, 0)
        self.speed = speed
        self.owner = owner
        self.damage = damage
        self.reflected = False
        self.dead = False

    def move(self, dt=1.0):
        """Move o projétil com base na direção e velocidade"""
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt

    def reflect(self, sword):
        """Reflete o projétil baseado no ângulo da espada"""
        # Calcula o vetor normal da espada
        sword_angle = math.radians(sword.sword_angle + sword.attack_rotation)
        normal = pg.math.Vector2(-math.sin(sword_angle), math.cos(sword_angle))
        
        # Reflete o vetor de direção
        self.direction = self.direction - 2 * self.direction.dot(normal) * normal
        self.reflected = True
        self.owner = sword.player  # Agora o projétil pertence ao jogador

    def is_on_map(self, map_width, map_height):
        """Verifica se o projétil ainda está dentro do mapa"""
        return (0 <= self.rect.x <= map_width and 
                0 <= self.rect.y <= map_height)

    def draw(self, surface, camera_offset=None):
        if camera_offset is None:
            camera_offset = [0, 0]
        pos = (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
        surface.blit(self.image, pos)

    def update(self, dt=1.0):
        self.move(dt)
        if hasattr(self.owner, 'game'):
            # Verifica se saiu do mapa
            if not self.is_on_map(self.owner.game.map.width, self.owner.game.map.height):
                self.dead = True
                return
                
            # Verifica colisão com o jogador se não foi refletido
            if not self.reflected and self.rect.colliderect(self.owner.game.player.rect):
                self.owner.game.player.take_damage(self.damage)
                self.dead = True