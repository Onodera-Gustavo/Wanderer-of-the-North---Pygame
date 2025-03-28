import pygame as pg


from settings import *


class Entidades:
    def __init__(self, game, name):
        self.game = game
        self.name = name
        
        
        self.can_move = True
        self.hurt = False
        self.dead = False
        self.can_get_hurt = True
        
            # Variáveis para Sprite dos inimigos
        # self.entity_animation = EntityAnimation(self)
        # self.path = f'./assets/characters/{self.name}'
        # self.animation_database = load_animation_sprites(f'{self.path}/')
        # self.image = pygame.transform.scale(pygame.image.load(f'{self.path}/idle/idle0.png'),utils.basic_entity_size).convert_alpha()
        # self.rect = self.image.get_rect()
        # self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        # self.velocity = [0, 0]
    
    def Esta_Morto(self):
        if self.current_hp <= 0 and self.dead is False:
            self.dead = True
            self.can_move = False
            self.can_get_hurt = False

    def can_move(self):
        return self.can_move
    
    def can_get_hurt(self):
        return self.can_get_hurt
    
    