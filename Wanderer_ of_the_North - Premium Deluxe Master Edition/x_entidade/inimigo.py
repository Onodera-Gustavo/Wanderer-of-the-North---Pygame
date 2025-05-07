import pygame as pg
import random

from settings import time_passed, cores
from x_entidade.entidade import *


class HealthBar:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.max_hp = max_hp
        self.hp = max_hp
        
    
    def update(self, vida, new_x=None, new_y=None):
        self.hp = vida
        if new_x is not None:
            self.x = new_x + 11
        if new_y is not None:
            self.y = new_y
    
    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pg.draw.rect(surface, cores['vermelho'], (self.x, self.y, self.w, self.h))
        pg.draw.rect(surface, cores['verde'], (self.x, self.y, self.w * ratio, self.h))
        

class Inimigo(Entidades):
    def __init__(self, game, nome, vida_max, defesa, velocidade_min, velocidade_max, sala, x, y, tipo='Mobs'):

        #print(f"Criando inimigo {nome} em ({x}, {y})")  # Debug de posição

        super().__init__(game, nome, tipo)  # Passa corretamente os argumentos para Entidades
        self.game = game
        self.nome = nome
        self.sala = sala
        

        # Atributos do inimigo
        self.defense = defesa
        self.vida_max = vida_max
        self.vida = self.vida_max
        self.speed = 0
        self.velocidades = [velocidade_min, velocidade_max]
        

        # Instancias de Movimentação
        self.fugindo = False
        self.ponto_fuga = None
        self.fuga_timer = 0

        self.perseguindo = False
        self.perseguindo_timer = 0

        # Tempos de ação
        self.attack_cooldown = 0
        self.attack_time = 1000
        self.weapon_hurt_cooldown = 0
        
        # Outros
        self.direction = False
        
        self.destination_position = None
        self.move_time = 0
        self.speed_change_interval = 1500  # ms
        self.flee_radius = 100  # raio para fugir do jogador
        self.chase_radius = 200  # raio para perseguir o jogador
        
        self.rect = pg.Rect(x, y, self.hitbox.width, self.hitbox.height) 
        self.health_bar = HealthBar(self.hitbox.centerx, self.hitbox.y, 30, 5, self.vida)

        self.mask = pg.mask.from_surface(self.image)
        self.hitbox = self.rect  

        self.collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        
    def can_attack(self):
        if time_passed(self.attack_cooldown, self.attack_time) and self.pode_atacar and not self.game.player.dead:
            #print(f"{self.nome} atacou!")
            return True
    def can_attack(self):
        if time_passed(self.attack_cooldown, self.attack_time) and self.pode_atacar and not self.game.player.dead:
            #print(f"{self.nome} atacou!")
            return True

    def update(self):
        """Atualiza o inimigo com delta time"""
        dt = self.game.dt
        
        self.basic_update()
        self.change_speed()
        self.mudar_instancia()
        self.basic_movement(dt)
        self.apply_movement(dt)  # Novo método para aplicar movimento com colisão
        self.attack_player(self.game.player)
        
        # Atualiza barra de vida
        bar_x = self.hitbox.centerx - self.health_bar.w // 2
        bar_y = self.hitbox.top - 10
        self.health_bar.update(self.vida, bar_x, bar_y)

    def change_speed(self):  # changes speed every 1.5s
        if time_passed(self.move_time, 1500):
            self.move_time = pg.time.get_ticks()
            self.speed = random.randint(self.velocidades[0], self.velocidades[1])
            return True

    def calcular_distancia(self, jogador):
        distancia = self.rect.centerx - jogador.rect.centerx, self.rect.centery - jogador.rect.centery # distância entre o jogador e o inimigo
        return pg.math.Vector2(distancia).length()
    
    def set_velocity(self, vector):
        if isinstance(vector, pg.math.Vector2):  # Se for Vector2
            self.velocity = [vector.x, vector.y]
        else:  # Se for lista/tupla
            self.velocity = [vector[0], vector[1]]
        
    def get_direction_vector(self, target):
        """Versão simplificada e mais robusta"""
        # Se for Vector2 (como destination_position)
        if isinstance(target, pg.math.Vector2):
            target_x, target_y = target.x, target.y
        # Se for um objeto com rect (como Player)
        elif hasattr(target, 'rect'):
            target_x, target_y = target.rect.centerx, target.rect.centery
        # Para outros casos (lista, tupla, etc)
        else:
            target_x, target_y = target[0], target[1]

        dir_vector = pg.math.Vector2(target_x - self.rect.centerx,
                                   target_y - self.rect.centery)
        if dir_vector.length_squared() > 0:
            dir_vector.normalize_ip()
        return dir_vector
        
    def pick_random_spot(self, min_distance=350):
        """Escolhe um ponto aleatório longe o suficiente do jogador"""
        min_x, max_x = self.game.sala.sala_x_min, self.game.sala.sala_x_max
        min_y, max_y = self.game.sala.sala_y_min, self.game.sala.sala_y_max
        
        player_pos = pg.math.Vector2(self.game.player.rect.centerx, self.game.player.rect.centery)
        
        while True:
            pick = pg.math.Vector2(random.randint(min_x, max_x), random.randint(min_y, max_y))
            vector = player_pos - pick
            if vector.length() >= min_distance:
                return pick
                
    def move_towards(self, target, dt):
        """Move-se na direção do alvo"""
        dir_vector = self.get_direction_vector(target)
        if dir_vector.length_squared() > 0:  # Verifica se o vetor tem comprimento > 0
            dir_vector.scale_to_length(self.speed * dt)
            self.set_velocity(dir_vector)
        else:
            self.set_velocity(pg.math.Vector2(0, 0))  # Se estiver na mesma posição, para de se mover
        
    def move_away_from(self, target, dt, radius):
        """Versão corrigida"""
        distance_to_target = self.calcular_distancia(target)
        
        if distance_to_target < radius:
            if not self.destination_position:
                self.destination_position = self.pick_random_spot()
                
            # Usa o Vector2 diretamente, sem criar Rect
            dir_vector = self.get_direction_vector(self.destination_position)
            if dir_vector.length_squared() > 0:  # Verifica se o vetor tem comprimento > 0
                dir_vector.scale_to_length(self.speed * dt)
                self.set_velocity(dir_vector)
            
            # Verifica se chegou perto do destino
            if (self.destination_position - pg.math.Vector2(self.rect.center)).length() < 10:
                self.destination_position = None
        else:
            self.set_velocity(pg.math.Vector2(0, 0))
            
    def basic_movement(self, dt):
        """Versão mais limpa"""
        if self.dead or not self.can_move or self.game.player.dead:
            self.set_velocity([0, 0])
            return
            
        if self.fugindo:
            self.move_away_from(self.game.player, dt, self.flee_radius)
        elif self.perseguindo:
            self.move_towards(self.game.player, dt)
        else:
            self.set_velocity([0, 0])
                
            #print(f"Movimento - Fugindo: {self.fugindo}, Perseguindo: {self.perseguindo}, Velocidade: {self.speed}") #DEBUG
            
            if self.fugindo:
                self.move_away_from(self.game.player, dt, self.flee_radius)
            elif self.perseguindo:
                self.move_towards(self.game.player, dt)

    def take_damage(self, damage):
        """ Reduz a vida do inimigo e atualiza a barra de vida """
        self.hurt = True
        self.hurt_time = pg.time.get_ticks()  
        self.vida = max(0, self.vida - damage)
        self.health_bar.update(self.vida)
    
    def is_dead(self):
        if self.dead and pg.time.get_ticks() - self.dead_time >= 10000:
            self.game.sala.inimigos.remove(self)
    
    # Atualize o método draw para compatibilidade com câmera:
    def draw(self, surface, camera_offset=None):
        """Desenha a barra de vida do inimigo com correção para câmera"""
        if camera_offset is None:
            camera_offset = [0, 0]
        
        # Ajusta a posição da barra de vida para considerar o offset da câmera
        health_bar_pos = (
            self.hitbox.centerx - self.health_bar.w//2 - camera_offset[0] + 10,
            self.hitbox.top - 10 - camera_offset[1]
        )
        
        # Cria uma superfície temporária para a barra de vida
        health_surface = pg.Surface((self.health_bar.w, self.health_bar.h), pg.SRCALPHA)
        
        # Desenha a barra de vida na superfície temporária
        ratio = self.health_bar.hp / self.health_bar.max_hp
        pg.draw.rect(health_surface, (255, 0, 0), (0, 0, self.health_bar.w, self.health_bar.h))  # Vermelho (fundo)
        pg.draw.rect(health_surface, (0, 255, 0), (0, 0, self.health_bar.w * ratio, self.health_bar.h))  # Verde (vida atual)
        
        # Desenha o inimigo
        pos = (
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1]
        )
        surface.blit(self.image, pos)

        # Desenha a superfície na tela principal
        surface.blit(health_surface, health_bar_pos)

        
    # def apply_movement(self, dt):
    #     """Aplica movimento com verificação de colisão"""
    #     self.old_rect = self.rect.copy()
        
    #     # Converte velocity para Vector2 se necessário
    #     velocity = pg.math.Vector2(self.velocity[0], self.velocity[1]) if isinstance(self.velocity, list) else self.velocity
        
    #     # Movimento em X
    #     self.rect.x += velocity.x * dt * 60  # Multiplica por 60 para normalizar
    #     self.hitbox.x += velocity.x * dt * 60
    #     self.check_map_collision('horizontal')
        
    #     # Movimento em Y
    #     self.rect.y += velocity.y * dt * 60
    #     self.hitbox.y += velocity.y * dt * 60
    #     self.check_map_collision('vertical')

    # def check_map_collision(self, direction):
    #     """Verifica colisão com o mapa"""
    #     if direction == 'horizontal':
    #         if self.game.map.check_collision(self):
    #             if self.velocity[0] > 0:  # Colisão à direita
    #                 self.rect.right = self.old_rect.right
    #                 self.collision_types['right'] = True
    #             elif self.velocity[0] < 0:  # Colisão à esquerda
    #                 self.rect.left = self.old_rect.left
    #                 self.collision_types['left'] = True
    #             self.hitbox.centerx = self.rect.centerx
    #             self.velocity[0] = 0
        
    #     elif direction == 'vertical':
    #         if self.game.map.check_collision(self):
    #             if self.velocity[1] > 0:  # Colisão abaixo
    #                 self.rect.bottom = self.old_rect.bottom
    #                 self.collision_types['bottom'] = True
    #             elif self.velocity[1] < 0:  # Colisão acima
    #                 self.rect.top = self.old_rect.top
    #                 self.collision_types['top'] = True
    #             self.hitbox.centery = self.rect.centery
    #             self.velocity[1] = 0
    
