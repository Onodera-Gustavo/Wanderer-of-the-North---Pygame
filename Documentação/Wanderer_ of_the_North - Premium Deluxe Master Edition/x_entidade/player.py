import pygame as pg
import math
from random import randint

from x_entidade.entidade import Entidades
from settings import *

class HealthBar:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.max_hp = max_hp
        self.hp = max_hp
    
    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pg.draw.rect(surface, (255, 0, 0), (self.x, self.y, self.w, self.h))
        pg.draw.rect(surface, (0, 255, 0), (self.x, self.y, self.w * ratio, self.h))
        pg.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.w, self.h), 2)

class Player(Entidades):
    def __init__(self, pos, game):
        nome = "Knight"
        tipo = "Especial"
        super().__init__(game, nome, tipo)
        
        self.rect = self.image.get_rect(center=pos)
        self.old_rect = self.rect.copy()
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.mask = pg.mask.from_surface(self.image)
        
        # Variáveis de movimento
        self.direction = pg.math.Vector2(0,0)
        self.last_direction = pg.math.Vector2(1, 0)
        
        # Atributos do jogador
        self.speed = 5.0
        self.dash = Dash(self)
        self.vida_max = 300
        self.vida = 300
        self.shield = 0  # Escudo inicial
        self.attack_cooldown = 350
        
        # Bônus
        self.tem_escudo = False
        self.pocao_magica = False
        self.pocao_timer = 0
        self.pocao_duracao = 10000  # 10 segundos
        
        self.health_bar = HealthBar(20, 20, 200, 20, self.vida_max)
        self.is_dead = False 
        
        
    def update_health_bar(self):
        self.health_bar.hp = self.vida

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
            self.last_direction = self.direction.copy()
        
        # Aplica efeito da poção de velocidade
        speed_multiplier = 1.5 if self.pocao_magica else 1.0
        if keys[pg.K_LSHIFT]:
            self.dash.start_dash(self.direction, self.last_direction, speed_multiplier)

    def update(self):
        if self.vida <= 0:
            self.is_dead = True
        self.old_rect = self.rect.copy()
        self.basic_update()
        
        self.movimentacao()
        self.dash.update()
        
        # Verifica se a poção expirou
        if self.pocao_magica and pg.time.get_ticks() - self.pocao_timer > self.pocao_duracao:
            self.pocao_magica = False
        
        # Aplica movimento
        if self.dash.dashing:
            self.velocity = self.dash.dash_direction * self.dash.dash_speed
        else:
            speed_multiplier = 1.5 if self.pocao_magica else 1.0
            self.velocity = pg.Vector2(
                self.direction.x * self.speed * speed_multiplier,
                self.direction.y * self.speed * speed_multiplier
            )

        self.rect.x += self.velocity.x
        if self.game.map.check_collision(self):
            self.rect.x = self.old_rect.x
        
        self.rect.y += self.velocity.y
        if self.game.map.check_collision(self):
            self.rect.y = self.old_rect.y

        self.update_hitbox()
        self.update_health_bar()

    def take_damage(self, amount):
        """Reduz a vida do jogador, considerando o escudo"""
        self.hurt = True
        self.hurt_time = pg.time.get_ticks()
        
        if self.tem_escudo:
            # Escudo absorve todo o dano
            self.tem_escudo = False
        else:
            self.vida = max(0, self.vida - amount)
            if self.vida <= 0:
                self.is_dead = True  # Apenas define como True, não chama como método
        
        self.update_health_bar()
                
    def draw(self, tela):
        """Desenha a barra de vida e escudo"""
        self.health_bar.draw(tela)
        
        # Desenha o escudo se ativo
        if self.tem_escudo:
            shield_rect = pg.Rect(20, 50, 200, 20)
            pg.draw.rect(tela, (0, 0, 255), shield_rect)
            pg.draw.rect(tela, (0, 0, 0), shield_rect, 2)
            
        # Desenha indicador de poção ativa
        if self.pocao_magica:
            remaining_time = max(0, self.pocao_duracao - (pg.time.get_ticks() - self.pocao_timer))
            ratio = remaining_time / self.pocao_duracao
            potion_rect = pg.Rect(20, 80, 200 * ratio, 10)
            pg.draw.rect(tela, (255, 0, 255), potion_rect)
            pg.draw.rect(tela, (0, 0, 0), pg.Rect(20, 80, 200, 10), 2)
            
    
    
    
class Dash:
    def __init__(self, player):
        self.player = player
        self.dashing = False
        self.dash_pressed = False
        
        self.base_dash_speed = 20
        self.dash_speed = self.base_dash_speed
        
        self.dash_timer = 0
        self.dash_duration = 10
        
        self.dash_cooldown_timer = 0
        self.dash_cooldown = 60
        self.dash_direction = pg.Vector2(0, 0)
        
    def start_dash(self, direction, last_direction, speed_multiplier=1.0):
        if self.dash_cooldown_timer == 0 and not self.dashing:
            self.dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            self.dash_speed = self.base_dash_speed * speed_multiplier
            
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




class Sword():
    def __init__(self, player):
        original_image = pg.image.load(BASE_DIR + r'\graphics\PixelCrawler\Weapons\espadinha.png').convert_alpha()
        self.original_image = pg.transform.scale(original_image, (original_image.get_width()//8, original_image.get_height()//6))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=player.rect.center)
        self.damage = 200
        self.radius = 50
        self.sword_angle = 0
        self.attack_rotation = 80
        self.attack_direction = 1
        self.attacking = False
        self.player = player
        self.hit_enemy = False

    def update(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        # Converte mouse para coordenadas mundiais
        mouse_world_x = mouse_x + self.player.game.camera_offset[0]
        mouse_world_y = mouse_y + self.player.game.camera_offset[1]
        
        mouse_vector = pg.Vector2(
            mouse_world_x - self.player.rect.centerx,
            mouse_world_y - self.player.rect.centery
        )

        if mouse_vector.length() > 0:
            self.sword_angle = math.degrees(math.atan2(mouse_vector.y, mouse_vector.x))

        if self.attacking:
            self.attack_rotation += 15 * self.attack_direction
            self.check_collision()
            self.check_projectile_collision()
            if abs(self.attack_rotation) >= 120:
                self.attacking = False
                self.hit_enemy = False
                self.attack_direction *= -1

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.hit_enemy = False

    def get_positions(self):
        angle_rad = math.radians(self.sword_angle + self.attack_rotation)
        direction_vector = pg.Vector2(math.cos(angle_rad), math.sin(angle_rad))

        # Posição relativa ao player (em coordenadas mundiais)
        base_radius = self.radius * 0.6
        handle_x = self.player.rect.centerx + direction_vector.x * base_radius
        handle_y = self.player.rect.centery + direction_vector.y * base_radius
        
        sword_tip_x = self.player.rect.centerx + direction_vector.x * self.radius
        sword_tip_y = self.player.rect.centery + direction_vector.y * self.radius

        return (handle_x, handle_y), (sword_tip_x, sword_tip_y)

    def check_collision(self):
        if self.hit_enemy:
            return False

        # Cria uma máscara temporária para a espada
        sword_mask = pg.mask.from_surface(self.image)
        
        for inimigo in self.player.game.sala.inimigos:
            # Calcula offset em coordenadas mundiais
            offset_x = inimigo.rect.x - self.rect.x
            offset_y = inimigo.rect.y - self.rect.y
            
            if sword_mask.overlap(inimigo.mask, (offset_x, offset_y)):
                self.hit_enemy = True
                inimigo.take_damage(self.damage)
                return True
        
        return False
    
    def check_projectile_collision(self):
        """Verifica colisão com projéteis e os reflete"""
        for inimigo in self.player.game.sala.inimigos:
            if hasattr(inimigo, 'projeteis'):
                for proj in inimigo.projeteis[:]:
                    if self.rect.colliderect(proj.rect) and not proj.reflected:
                        proj.reflect(self)
                        return True
        return False

    def draw(self, surface):
        """Desenha a espada na superfície especificada"""
        angle_deg = self.sword_angle + self.attack_rotation + 90
        rotated_image = pg.transform.rotozoom(self.original_image, -angle_deg, 1)
        
        # Obtém posições em coordenadas mundiais
        (handle_x, handle_y), _ = self.get_positions()
        
        # Converte para coordenadas de tela (subtraindo o offset da câmera)
        draw_x = handle_x - self.player.game.camera_offset[0]
        draw_y = handle_y - self.player.game.camera_offset[1]
        
        # Atualiza rect e image
        self.image = rotated_image
        self.rect = rotated_image.get_rect(center=(handle_x, handle_y))  # Mantém em coordenadas mundiais
        
        # Desenha na posição correta da tela
        surface.blit(rotated_image, (draw_x - rotated_image.get_width()/2, 
                                    draw_y - rotated_image.get_height()/2))
    
    def change_sprite(self, new_sprite_path):
        try:
            new_img = pg.image.load(new_sprite_path).convert_alpha()
            new_img = pg.transform.scale(new_img, (new_img.get_width() // 5, new_img.get_height() // 4))
            self.original_image = new_img
            self.image = new_img.copy()
            self.rect = self.image.get_rect(center=self.rect.center)
            print("Sprite da espada alterado com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar novo sprite: {new_sprite_path} -> {e}")




