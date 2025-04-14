import pygame as pg
import math
import os
from random import randint

from settings import *
# Classe da Barra de Vida
# class HealthBar:
#     def __init__(self, x, y, w, h, max_hp):
#         self.x = x
#         self.y = y
#         self.w = w
#         self.h = h
#         self.max_hp = max_hp
#         self.hp = max_hp
    
#     def update(self, current_hp):
#         self.hp = current_hp
    
#     def draw(self, surface):
#         ratio = self.hp / self.max_hp
#         pg.draw.rect(surface, cores['vermelho'], (self.x, self.y, self.w, self.h))
#         pg.draw.rect(surface, cores['verde'], (self.x, self.y, self.w * ratio, self.h))



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
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        original_image = pg.image.load(BASE_DIR + r'\pixil-frame-0 (2).png').convert_alpha()
        
        self.image = pg.transform.scale(original_image, (original_image.get_width()//4, original_image.get_height()//4))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = get_mask_rect(self.image, * self.rect.topleft)
        
        self.direction = pg.math.Vector2(0,1)
        self.last_direction = pg.math.Vector2(1, 0)  # Inicializa com uma direção padrão
        self.speed = 3.5
        self.dash = Dash(self)
        self.health = 100
        self.shield = 100
        self.attack_cooldown = 350

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
        
        if keys[pg.K_LSHIFT]:
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
            self.death()
        
    def death(self):
        print("Você morreu!")
        pass


class Sword(pg.sprite.Sprite):
    def __init__(self, player):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        original_image = pg.image.load(BASE_DIR + r'\PixelCrawler\Weapons\espadinha.png').convert_alpha()

        self.image = pg.transform.scale(original_image, (original_image.get_width(), original_image.get_height()))
        self.rect = self.image.get_rect(center=player.rect.center)  # Use player.rect.center here
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)

        self.radius = 50
        self.sword_angle = 0  # Variável para a direção da espada
        self.attack_rotation = 100  # Rotação inicial do ataque
        self.attack_direction = 1  # Direção do ataque (1 para direita, -1 para esquerda)
        self.attacking = False
        self.player = player
        self.hit_enemy = False  # Flag para impedir múltiplos hits no mesmo ataque




    def update(self):
    # Pega a posição do mouse
        mouse_x, mouse_y = pg.mouse.get_pos()

        # Calcula o vetor direção do jogador até o mouse
        mouse_vector = pg.Vector2(mouse_x - self.player.rect.centerx, mouse_y - self.player.rect.centery)

        # Calcula o ângulo para o mouse
        if mouse_vector.length() > 0:
            self.sword_angle = math.degrees(math.atan2(mouse_vector.y, mouse_vector.x))  # Converte para graus e atualiza

        if self.attacking:
            # Se o ataque está em progresso, aplica um pequeno movimento de rotação
            self.attack_rotation += 15 * self.attack_direction  

            # Se a rotação atingir o limite, finaliza o ataque
            if abs(self.attack_rotation) >= 100:
                self.attack_rotation = 100 * self.attack_direction
                self.attacking = False
                self.hit_enemy = False
                self.attack_direction *= -1


    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.hit_enemy = False  # Permite que o próximo ataque cause dano

    def get_positions(self):
        """ Retorna as coordenadas do cabo e da ponta da espada ajustadas pela câmera """
        angle_rad = math.radians(self.sword_angle + self.attack_rotation)  # Converte o ângulo para radianos
        
        # Vetor unitário para a direção da espada
        direction_vector = pg.Vector2(math.cos(angle_rad), math.sin(angle_rad))

        # Ajusta a posição inicial 15 pixels para baixo
        handle_x = self.player.rect.centerx
        handle_y = self.player.rect.centery + 15

        # Corrige a ponta da espada para manter o tamanho correto
        sword_tip_x = handle_x + direction_vector.x * self.radius
        sword_tip_y = handle_y + direction_vector.y * self.radius

        # Ajusta a posição pela câmera
        return (handle_x, handle_y), (sword_tip_x , sword_tip_y )




    def check_collision(self, inimigos_gerados):
        """Verifica se qualquer parte da espada atinge um inimigo"""
        if self.hit_enemy:  # Se já acertou, não pode causar outro hit
            return False

        (x1, y1), (x2, y2) = self.get_positions()  # Obtém as posições do ataque
        step = 5  # Define o intervalo dos pontos na linha da espada

        for i in range(0, 101, step):  # Percorre a trajetória do ataque
            px = x1 + (x2 - x1) * i / 100  # Calcula a posição x do ponto
            py = y1 + (y2 - y1) * i / 100  # Calcula a posição y do ponto
            
            for inimigo in inimigos_gerados:  # Percorre todos os inimigos
                if inimigo.rect.collidepoint(px, py):  # Se houver colisão
                    self.hit_enemy = True  # Marca que já houve um hit
                    return True

        return False  # Retorna False se nenhum inimigo foi atingido


    def draw(self, surface):
        pg.draw.line(surface, cores['branco'], *self.get_positions(), 5)

