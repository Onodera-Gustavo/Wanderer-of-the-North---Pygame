import pygame as pg
import os
import random

from settings import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Entidades:
    def __init__(self, game, nome):
        self.game = game
        self.nome = nome
        self.path = os.path.join(BASE_DIR, "PixelCrawler", "Entities", "Mobs", self.nome)
        self.animation_database = load_animation_sprites(self.path)
        
        if "IDLE" not in self.animation_database or not self.animation_database["IDLE"]:
            print(f"Erro: Nenhuma animação 'IDLE' encontrada no caminho {self.path}")
            self.image = pg.Surface(basic_entity_size)  # Cria um espaço em branco como fallback
        else:
            self.image = self.animation_database["IDLE"][0]

        self.rect = self.image.get_rect()
        self.hitbox = get_mask_rect(self.image, * self.rect.topleft)
        self.can_get_hurt = True
        self.can_move = True
        self.dead = False
        self.entity_animation = EntityAnimation(self)

        self.move_time = 0
        self.attack_cooldown = 0
        self.weapon_hurt_cooldown = 0
        self.dead_time = 0

        self.velocity = [0, 0]

    def __repr__(self):
        return self.nome
    
    def can_attack(self):
        if time_passed(self.attack_cooldown, 1000):
            self.attack_cooldown = pg.time.get_ticks()
            return True

    def can_get_hurt_from_weapon(self):
        if time_passed(self.weapon_hurt_cooldown, self.game.player.attack_cooldown):
            return True

    def attack_player(self, player):
        if self.hitbox.colliderect(
                player.hitbox) and self.can_attack() and not self.game.world_manager.switch_room and not self.hurt:
            player.calculate_collision(self)
    
    def esta_morto(self):
        """Verifica se o inimigo está morto."""
        if self.current_hp <= 0 and not self.dead:
            self.dead = True
            self.can_move = False
            self.dead_time = pg.time.get_ticks()
            
    def basic_update(self):
        self.esta_morto()
        self.update_hitbox()
        self.entity_animation.update()
        
        
    def change_speed(self):  # changes speed every 1.5s
        if time_passed(self.move_time, 1500):
            self.move_time = pg.time.get_ticks()
            self.speed = random.randint(10, 200)
            return True

    def update_hitbox(self):
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox.midbottom = self.rect.midbottom

    # def new_move(self):
    #     """Atualiza a posição do inimigo."""
    #     if self.velocity[0] != 0 or self.velocity[1] != 0:
            


def load_animation_sprites(base_path, size=basic_entity_size):
    """Carrega animações a partir de sprite sheets (Idle, Run, Death)."""
    animation_data = {"IDLE": [], "RUN": [], "DEATH": []}
    
    for state in ["Idle", "Run", "Death"]: 
        state_path = os.path.join(base_path, state)
        if os.path.exists(state_path):
            for sprite_file in os.listdir(state_path):
                sheet_path = os.path.join(state_path, sprite_file)
                
                # Verifica se o arquivo existe e imprime o caminho
                if not os.path.exists(sheet_path):
                    print(f"ERRO: Arquivo não encontrado: {sheet_path}")
                    continue
                
                # print(f"Carregando sprite: {sheet_path}")  # DEBUG

                try:
                    sprite_sheet = pg.image.load(sheet_path).convert_alpha()
                except Exception as e:
                    print(f"Erro ao carregar imagem {sheet_path}: {e}")
                    continue
                
                frames_count = sprite_sheet.get_width() // 32  # Usa o tamanho real do frame
                if frames_count == 0:
                    print(f"ERRO: A sprite sheet {sheet_path} não tem frames suficientes!")
                    continue
                
                sprite_width = sprite_sheet.get_width() // frames_count
                sprite_height = sprite_sheet.get_height()
                
                # print(f"{sheet_path} tem {frames_count} frames.")

                frames = [
                    pg.transform.scale(
                        sprite_sheet.subsurface((i * sprite_width, 0, sprite_width, sprite_height)),
                        size
                    )
                    for i in range(frames_count)
                ]
                
                animation_data[state.upper()].extend(frames)

    
    return animation_data




class EntityAnimation:
    def __init__(self, entity, death_anim=6, speed=25):
        self.entity = entity

        self.animation_direction = 'right'
        self.animation_frame = 0
        self.death_animation_frames = death_anim
        self.speed = speed

    def moving(self) -> bool:
        return bool(sum(self.entity.velocity))
        

    def get_direction(self):
        self.animation_direction = 'right' if self.entity.direction else 'left'
        

    def update_animation_frame(self):
        self.animation_frame += 1 / self.speed if self.moving() else 0.5 / self.speed
        if self.animation_frame >= len(self.entity.animation_database["RUN"]):
            self.animation_frame = 0
        estado_atual = "IDLE" if not self.moving() else "RUN"
        
        if self.animation_frame >= len(self.entity.animation_database[estado_atual]):
            self.animation_frame = 0  # Reinicia a animação corretamente
        
    def animation(self, state):
        """Animation if idle"""
        self.update_animation_frame()
        self.get_direction()
        if self.animation_direction == 'left':
            self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
            self.entity.image = pg.transform.flip(self.entity.image, 1, 0)
        elif self.animation_direction == 'right':
            self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
            

    def animation_test(self, state):
        if self.animation_frame == 0:  # Define um frame inicial aleatório apenas no início
            self.animation_frame = random.randint(0, len(self.entity.animation_database[state]) - 1)
        self.update_animation_frame()
        self.get_direction()
        if self.animation_direction == 'left':
            self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
            self.entity.image = pg.transform.flip(self.entity.image, 1, 0)
        elif self.animation_direction == 'right':
            self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]

    def death_animation(self):
        """Animação de morte."""
        self.animation_frame += 1.0 / self.speed
        if self.animation_frame >= len(self.entity.animation_database["DEATH"]):
            self.animation_frame = len(self.entity.animation_database["DEATH"]) - 1
            if time_passed(self.entity.dead_time, 10000):  # Espera 10 segundos
                self.entity.is_dead()
            

        self.entity.image = self.entity.animation_database["DEATH"][int(self.animation_frame)]
        self.entity.image = pg.transform.flip(self.entity.image, 1, 0) if self.animation_direction == 'left' else self.entity.image
        

    def choice_animation(self):
        """Define a animação com base no estado do inimigo."""
        if self.entity.dead:
            self.death_animation()
        elif self.moving():
            self.animation_test("RUN")    
        else:
            self.animation("IDLE")

    def update(self):
        self.choice_animation()
