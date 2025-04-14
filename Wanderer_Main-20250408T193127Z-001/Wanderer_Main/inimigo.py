import pygame as pg
import random
from settings import *
from entidade import *


class HealthBar:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.max_hp = max_hp
        self.hp = max_hp
    
    def update(self, current_hp, new_x=None, new_y=None):
        self.hp = current_hp
        if new_x is not None:
            self.x = new_x + 11
        if new_y is not None:
            self.y = new_y
    
    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pg.draw.rect(surface, cores['vermelho'], (self.x, self.y, self.w, self.h))
        pg.draw.rect(surface, cores['verde'], (self.x, self.y, self.w * ratio, self.h))



class Inimigo(Entidades):
    def __init__(self, game, classe, nome, sala, x, y):
        super().__init__(game, nome)  # Passa corretamente os argumentos para Entidades
        self.game = game
        self.nome = nome
        self.classe = classe
        self.sala = sala
        self.stats = ENEMY_STATS.get(nome, {})

        # Atributos do inimigo
        self.attack = self.stats.get('ataques', 10)
        self.speed = self.stats.get('velocidade', 1.0) 
        self.defense = self.stats.get('defesa', 0)
        self.max_hp = self.stats.get('vida', 100)
        self.current_hp = self.max_hp
        self.health_bar = HealthBar(self.hitbox.centerx, self.hitbox.y, 30, 5, self.current_hp)
        
        self.move_time = 0
        self.attack_cooldown = 0
        self.weapon_hurt_cooldown = 0
        
        self.direction = False
        
        self.rect = pg.Rect(x, y, self.hitbox.width, self.hitbox.height)
        
    
    def can_attack(self):
        if time_passed(self.attack_cooldown, 1000):
            self.attack_cooldown = pg.time.get_ticks()
            return True

    def can_get_hurt_from_weapon(self):
        if time_passed(self.weapon_hurt_cooldown, self.game.player.attack_cooldown):
            return True

    def attack_player(self, player):
        if self.hitbox.colliderect(player.hitbox) and self.can_attack() and self.can_get_hurt_from_weapon():
            self.realizar_ataque(player)

    def update(self):
        self.basic_update()
        self.change_speed()
        self.perseguir(self.game.player)
        self.attack_player(self.game.player)

        # Centraliza a barra de vida com base no centro do hitbox
        bar_x = self.hitbox.centerx - self.health_bar.w // 2
        bar_y = self.hitbox.top - 10
        self.health_bar.update(self.current_hp, bar_x, bar_y)

        
    def change_speed(self):  # changes speed every 1.5s
        if time_passed(self.move_time, 1500):
            self.move_time = pg.time.get_ticks()
            self.speed = random.randint(10, 100)
            return True

    def perseguir(self, jogador):
        """Movimenta o inimigo na direção do centro do jogador."""
        centro_jogador_x = jogador.rect.centerx
        centro_jogador_y = jogador.rect.centery
        centro_inimigo_x = self.rect.centerx
        centro_inimigo_y = self.rect.centery

        movimento_x = 0
        movimento_y = 0

        if self.can_move:
            if centro_inimigo_x < centro_jogador_x:
                movimento_x = min(self.speed * 0.02, abs(centro_inimigo_x - centro_jogador_x))
                self.rect.x += movimento_x
                self.direction = True
            elif centro_inimigo_x > centro_jogador_x:
                movimento_x = -min(self.speed * 0.02, abs(centro_inimigo_x - centro_jogador_x))
                self.rect.x += movimento_x
                self.direction = False

            if centro_inimigo_y < centro_jogador_y:
                movimento_y = min(self.speed * 0.02, abs(centro_inimigo_y - centro_jogador_y))
                self.rect.y += movimento_y
            elif centro_inimigo_y > centro_jogador_y:
                movimento_y = -min(self.speed * 0.02, abs(centro_inimigo_y - centro_jogador_y))
                self.rect.y += movimento_y

        # Salva velocidade real para a animação
        self.velocity = [movimento_x, movimento_y]
        

    def realizar_ataque(self, player):
        """ Ataca o jogador caso esteja em contato """
        if self.hitbox.colliderect(player.hitbox) and self.can_attack() and self.can_get_hurt_from_weapon():
            player.take_damage(self.attack)
            self.attack_cooldown = pg.time.get_ticks()
            self.weapon_hurt_cooldown = pg.time.get_ticks()

    def take_damage(self, damage):
        """ Reduz a vida do inimigo e atualiza a barra de vida """
        self.current_hp = max(0, self.current_hp - damage)
        self.health_bar.update(self.current_hp)
    
    def draw(self, tela):
        """Desenha o inimigo e sua barra de vida centralizada na tela."""
        if self.image:
            tela.blit(self.image, (self.rect.x, self.rect.y))
        self.health_bar.draw(tela)
    
    def is_dead(self):
        if self.dead:
            self.game.sala.inimigos.remove(self)
            print(f"{self.nome} foi derrotado!")




# Subclasses de inimigos
class EsqueletoSoldado(Inimigo):
    def __init__(self, game, sala, x, y):
        super().__init__(game, "Soldado", "EsqueletoSoldado", sala, x, y)

class Orco(Inimigo):
    def __init__(self, game, sala, x, y):
        super().__init__(game, "Soldado", "Orco", sala, x, y)

class EsqueletoArqueiro(Inimigo):
    def __init__(self, game, sala, x, y):
        super().__init__(game, "Atirador", "EsqueletoArqueiro", sala, x, y)


# Dicionário de classes de inimigos
CLASSES_INIMIGOS = {
    "Esqueleto Soldado": EsqueletoSoldado,
    "Orco": Orco,
    "Esqueleto Arqueiro": EsqueletoArqueiro

}


# Dicionário com os atributos de cada inimigo
ENEMY_STATS = {
    # Soldados
    'Esqueleto Soldado': {'vida': 120, 'defesa': 3, 'ataques': 10, 'velocidade': 0.6},
    'Orco': {'vida': 150, 'defesa': 6, 'ataques': 20, 'velocidade': 0.7},
    
    # # Atiradores
    'Esqueleto Arqueiro': {'vida': 80, 'defesa': 1, 'ataques': 7, 'velocidade': 0.7}
}

# BOSS_ENEMY_STATS = {
#     'Necromancer': {'vida': 300, 'defesa': 10, 'ataques': 25, 'velocidade': 0.4},
# }
