import pygame as pg
import random

from settings import *
from entidade import *

class Inimigo(Entidades):
    def __init__(self, game, classe, nome, sala):
        self.game = game
        self.nome = nome
        self.classe = classe
        self.sala = sala
        self.stats = ENEMY_STATS.get(nome, {})
        
        # Atributos do inimigo baseados no dicionário de estatísticas
        self.attack = self.stats.get('ataques', 10)
        self.speed = self.stats.get('velocidade', 1.0) * 100  # Convertendo para uma escala adequada
        self.defense = self.stats.get('defesa', 0)
        self.max_hp = self.stats.get('vida', 100)
        self.current_hp = self.max_hp
        
    def get_hurt(self, damage):
        if self.can_get_hurt:
            self.current_hp -= damage
            self.hurt = True
            self.can_get_hurt = False
            self.game.time = pg.time.get_ticks()

    def receber_dano(self, dano):
        """ Reduz a vida do inimigo levando em conta a defesa """
        dano_real = max(0, dano - self.defense)
        self.current_hp -= dano_real
        if self.current_hp <= 0:
            self.morrer()

    def morrer(self):
        """ Lógica para quando o inimigo morre """
        pass

    def update(self):
        """Função fictícia para atualizar o estado do inimigo no jogo"""
        pass 

    def spawn(self):
        self.rect.x = random.randint(200, 1000)
        self.rect.y = random.randint(250, 600)
    
    def draw(self):
        """Função fictícia para desenhar o inimigo no jogo"""
        pass 


class Soldado(Inimigo):
    def __init__(self, game, nome, sala):
        super().__init__(game, "Soldado", nome, sala)

    def atacar(self):
        pass

# Inimigos da Classe 'Soldado'
class EsqueletoSoldado(Soldado):
    def __init__(self, game, sala):
        super().__init__(game, "Esqueleto Soldado", sala)

        
class Demonio(Soldado):
    def __init__(self, game, sala):
        super().__init__(game, "Demônio", sala)
        
class Aberracao(Soldado):
    def __init__(self, game, sala):
        super().__init__(game, "Aberração", sala)

class Orco(Soldado):
    def __init__(self, game, sala):
        super().__init__(game, "Orco", sala)

class Goblin(Soldado):
    def __init__(self, game, sala):
        super().__init__(game, "Goblin", sala)

class MorcegoGigante(Soldado):
    def __init__(self, game, sala):
        super().__init__(game, "Morcego Gigante", sala)


class Atirador(Inimigo):
    def __init__(self, game, nome, sala):
        super().__init__(game, "Atirador", sala)
    
    def Atirar(self):
        pass

# Inimigos da Classe 'Atirador'
class EsqueletoArqueiro(Atirador):
    def __init__(self, game, sala):
        super().__init__(game, "Esqueleto Arqueiro", sala)
        
class CultistaIniciado(Atirador):
    def __init__(self, game, sala):
        super().__init__(game, "Cultista Iniciado", sala)

class CultistaSacerdote(Atirador):
    def __init__(self, game, sala):
        super().__init__(game, "Cultista Sacerdote", sala)
        
class CultistaDiaco(Atirador):
    def __init__(self, game, sala):
        super().__init__(game, "Cultista Diácono", sala)


# Dicionário com os atributos de cada inimigo
ENEMY_STATS = {
    # Soldados
    'Esqueleto Soldado': {'vida': 120, 'defesa': 3, 'ataques': 10, 'velocidade': 0.6},
    'Demônio': {'vida': 100, 'defesa': 5, 'ataques': 15, 'velocidade': 0.5},
    'Aberração': {'vida': 170, 'defesa': 8, 'ataques': 50, 'velocidade': 0.2},
    'Orco': {'vida': 150, 'defesa': 6, 'ataques': 20, 'velocidade': 0.7},
    'Goblin': {'vida': 100, 'defesa': 4, 'ataques': 15, 'velocidade': 0.6},
    'Morcego Gigante': {'vida': 50, 'defesa': 1, 'ataques': 10, 'velocidade': 1.0},
    
    # Atiradores
    'Esqueleto Arqueiro': {'vida': 80, 'defesa': 1, 'ataques': 7, 'velocidade': 0.7},
    'Cultista Iniciado': {'vida': 120, 'defesa': 2, 'ataques': 15, 'velocidade': 0.7},
    'Cultista Sacerdote': {'vida': 80, 'defesa': 4, 'ataques': 20, 'velocidade': 0.5},
    'Cultista Diácono': {'vida': 30, 'defesa': 5, 'ataques': 40, 'velocidade': 0.3},
}

# BOSS_ENEMY_STATS = {
#     'Necromancer': {'vida': 300, 'defesa': 10, 'ataques': 25, 'velocidade': 0.4},
# }

CLASSES_INIMIGOS = {
    # Soldados
    "Esqueleto Soldado": EsqueletoSoldado,
    "Demônio": Demonio,
    'Aberração': Aberracao,
    'Orco': Orco,
    'Goblin': Goblin,
    'Morcego Gigante': MorcegoGigante,
    
    # Atiradores
    "Esqueleto Arqueiro": EsqueletoArqueiro,
    'Cultista Iniciado': CultistaIniciado,
    "Cultista Sacerdote": CultistaSacerdote,
    'Cultista Diácono': CultistaDiaco
}

def escolher_inimigo_aleatorio(game, sala):
    """Escolhe um inimigo aleatório e retorna uma instância dele."""
    nome_inimigo = random.choice(list(CLASSES_INIMIGOS.keys()))
    classe_inimigo = CLASSES_INIMIGOS[nome_inimigo]
    return classe_inimigo(game, sala)

# Classe para gerenciar a Existência dos Inimigos nas suas respectivas salas
class OrdemInimigos:
    def __init__(self, game, sala, andar):
        self.game = game
        self.sala = sala
        
        self.inimigos_em_combate = []
        self.status_dano = 0.5 * andar
        self.status_vida = 4 * andar
        self.status_defesa = 1 * andar
    
    def desenhar_inimigos(self):
        for inimigo in self.sala:
            inimigo.draw()
            
    def ordenar_inimigos_em_combate(self):
        self.inimigos_em_combate = list(self.sala)

    def atualizar_inimigos(self):
        self.ordenar_inimigos_em_combate()
        for inimigo in self.sala:
            inimigo.update()
        # self.debug()

    def set_dano_inimigo(self, inimigo):
        inimigo.attack *= self.status_dano

    def set_vida_inimigo(self, inimigo):
        inimigo.max_hp *= self.status_vida
        inimigo.current_hp *= self.status_vida

    def aprimorar_inimigo(self, inimigo):
        self.set_vida_inimigo(inimigo)
        self.set_dano_inimigo(inimigo)

    def adicionar_inimigos_normais(self, sala, andar):
        num_de_inimigos = random.randint(1, 3 * andar) 
        
        for _ in range(num_de_inimigos):
            inimigo = escolher_inimigo_aleatorio(self.game, sala)
            sala.inimigos_em_combate.append(inimigo)
            self.aprimorar_inimigo(inimigo)
            inimigo.spawn()

    # def debug(self):
    #     if pg.mouse.get_pressed()[2]:
    #         mx, my = pg.mouse.get_pos()
    #         mx -= 64  # Ajuste da posição para renderização correta
    #         my -= 32
    #         novo_inimigo = escolher_inimigo_aleatorio(self.game, self.game.world_manager.current_room)
    #         self.game.world_manager.current_room.inimigos_em_combate.append(novo_inimigo)
    #         novo_inimigo.rect.topleft = (mx, my)