import pygame as pg
import os
import random

from settings import BASE_DIR, basic_entity_size, get_mask_rect, time_passed



class Entidades:
    def __init__(self, game, nome, tipo):
        self.game = game
        self.nome = nome
        self.tipo = tipo
        self.path = os.path.join(BASE_DIR, "graphics", "PixelCrawler", "Entities", self.tipo, self.nome)
        self.animation_database = load_animation_sprites(self.path)
        
    # if "HURT" not in self.animation_database or not self.animation_database["HURT"]:
    #     print(f"Erro: Nenhuma animação 'HURT' encontrada no caminho {self.path}")
    #     self.image = pg.Surface(basic_entity_size)  # Cria um espaço em branco como fallback
    # else:
        self.image = self.animation_database["IDLE"][0]

        self.rect = self.image.get_rect()
        self.hitbox = get_mask_rect(self.image, * self.rect.topleft)
        
        # variáveis de permissão
        self.can_move = True
        self.dead = False
        self.pode_atacar = True
        self.hurt = False

        # Variáveis de tempo
        self.move_time = 0
        self.attack_cooldown = 0
        self.weapon_hurt_cooldown = 0
        self.dead_time = 0
        self.hurt_time = 0
        

        self.velocity = [0, 0]
        self.entity_animation = EntityAnimation(self)
        self.animation_complete = False  # Adicione este atributo

    def __repr__(self):
        return self.nome
    
    def esta_morto(self):
        """Verifica se o inimigo está morto."""
        if self.vida <= 0 and not self.dead:
            self.dead = True
            self.can_move = False
            self.pode_atacar = False
            self.dead_time = pg.time.get_ticks()         
            
    def apply_movement(self, dt):
        """Aplica o movimento baseado na velocidade e delta time"""
        if not hasattr(self, 'velocity'):
            return
            
        # Converte velocity para Vector2 se necessário
        velocity = pg.math.Vector2(self.velocity[0], self.velocity[1]) if isinstance(self.velocity, list) else self.velocity
        
        # Aplica o movimento
        self.rect.x += velocity.x * dt * 60  # Multiplica por 60 para normalizar
        self.rect.y += velocity.y * dt * 60
        self.hitbox.center = self.rect.center      
            
    def basic_update(self):
        self.esta_morto()
        self.update_hitbox()
        self.entity_animation.update()

    def update_hitbox(self):
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.hitbox.midbottom = self.rect.midbottom
        self.mask = pg.mask.from_surface(self.image)  # Atualiza a mask


def load_animation_sprites(base_path, size=basic_entity_size):
    """Carrega animações a partir de sprite sheets (Idle, Run, Death)."""
    animation_data = {"IDLE": [], "RUN": [], "DEATH": [], "HURT": []}
    
    for state in ["Idle", "Run", "Death", "Hurt"]: 
        state_path = os.path.join(base_path, state)
        if os.path.exists(state_path):
            for sprite_file in os.listdir(state_path):
                sheet_path = os.path.join(state_path, sprite_file)
                
                # Verifica se o arquivo existe e imprime o caminho
                if not os.path.exists(sheet_path):
                    print(f"ERRO: Arquivo não encontrado: {sheet_path}")
                    continue
                
                #print(f"Carregando sprite: {sheet_path}")  # DEBUG

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
                
                #print(f"{sheet_path} tem {frames_count} frames.") # DEBUG caminho das sprites seus frames

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
        if self.entity.velocity[0] < 0:
            self.animation_direction = 'left'
        elif self.entity.velocity[0] > 0:
            self.animation_direction = 'right'


    def update_animation_frame(self, state):
        self.animation_frame += 2 / self.speed if self.moving() else 0.5 / self.speed
        if self.animation_frame >= len(self.entity.animation_database[state]):
            self.animation_frame = 0
        
    def animation(self, state):
        if self.animation_frame == 0 and state != "HURT":  # Define um frame inicial aleatório apenas no início
            self.animation_frame = random.randint(0, len(self.entity.animation_database[state]) - 1)
        self.update_animation_frame(state)
        self.get_direction()
        
        if self.animation_direction == 'left':
            self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]
            self.entity.image = pg.transform.flip(self.entity.image, 1, 0)
            
        elif self.animation_direction == 'right':
            self.entity.image = self.entity.animation_database[state][int(self.animation_frame)]

    def death_animation(self):
        """Animação de morte."""
        self.animation_frame += 0.8 / self.speed
        
        if self.animation_frame >= len(self.entity.animation_database["DEATH"]):
            self.animation_frame = len(self.entity.animation_database["DEATH"]) - 1
            self.entity.animation_complete = True  # Marca como completa
            
        self.entity.image = self.entity.animation_database["DEATH"][int(self.animation_frame)]
        self.entity.image = pg.transform.flip(self.entity.image, 1, 0) if self.animation_direction == 'left' else self.entity.image
        
    def hurt_animation(self):
        self.animation('HURT')
        if time_passed(self.entity.hurt_time, 200):
            self.entity.hurt = False
        
    def choice_animation(self):
        """Define a animação com base no estado do inimigo."""
        if self.entity.dead:
            self.death_animation()
        elif self.entity.hurt:
            self.hurt_animation()  # Dá prioridade à animação de dano
        elif self.moving():
            self.animation("RUN")
        else:
            self.animation("IDLE")

    def update(self):
        self.choice_animation()
