import pygame as pg
import random

from settings import time_passed
from x_entidade.inimigo import Inimigo
from x_entidade.boss import Boss
from x_entidade.projeteis import Projectile



class Soldado(Inimigo):
    def __init__(self, game, nome, vida_max, defesa, dano, velocidade_min, velocidade_max, sala, x, y):
        super().__init__(game, nome, vida_max, defesa, velocidade_min, velocidade_max, sala, x, y )
        
        self.dano = dano
        self.distancia_ataque = 20  # distância para ataque corpo-a-corpo
        
    def mudar_instancia(self):
        """Comportamento mais claro"""
        vida_ratio = self.vida / self.vida_max
        distancia = self.calcular_distancia(self.game.player)
        
        # Comportamento de fuga com pouca vida
        if vida_ratio <= 0.2 and not self.fugindo:
            if pg.time.get_ticks() - self.fuga_timer > 8000 and random.random() < 0.05:
                self.fugindo = True
                self.perseguindo = False
                self.destination_position = None
                self.fuga_timer = pg.time.get_ticks()
        # Comportamento normal
        else:
            self.fugindo = False
            self.perseguindo = distancia > self.distancia_ataque
        
    def attack_player(self, player):
        distancia = self.calcular_distancia(player)
        if distancia < self.distancia_ataque and not self.dead and not self.game.player.dead:
            self.realizar_ataque(player)
            
    def realizar_ataque(self, player):
        """ Ataca o player caso esteja em contato """
        if self.hitbox.colliderect(player.hitbox) and self.can_attack():
            player.take_damage(self.dano)
            self.attack_cooldown = pg.time.get_ticks()
           


class Atirador(Inimigo):
    def __init__(self, game, nome, vida_max, defesa, dano, velocidade_min, velocidade_max, sala, x, y):
        super().__init__(game, nome, vida_max, defesa, velocidade_min, velocidade_max, sala, x, y)
        
        self.projeteis = []
        self.tempo_ultimo_tiro = 0
        self.tempo_entre_tiros = 800
        self.dano_projetil = dano
        
        self.distancia_ataque = 350
        self.safe_distance = 300
        
    def mudar_instancia(self):
        distancia = self.calcular_distancia(self.game.player)
        
        if distancia < self.safe_distance:
            self.fugindo = True
            self.perseguindo = False
        elif distancia > self.distancia_ataque:
            self.fugindo = False
            self.perseguindo = True
        else:  # Distância ideal
            self.fugindo = False
            self.perseguindo = False
            self.set_velocity(pg.math.Vector2(0, 0))

    def disparar_projétil(self, player):
        agora = pg.time.get_ticks()
        #print({self.nome}, {agora}, {self.tempo_ultimo_tiro}, {self.tempo_entre_tiros})
        
        if agora - self.tempo_ultimo_tiro >= self.tempo_entre_tiros:
            direcao = pg.math.Vector2(
                player.rect.centerx - self.rect.centerx,
                player.rect.centery - self.rect.centery
            )
            proj = Projectile(
                    self.rect.centerx, 
                    self.rect.centery,
                    direcao,
                    speed=6,
                    owner=self,
                    damage=self.dano_projetil
                    #size=self.tamanho_projetil,
                    #color=self.cor_projetil
                )
            
            self.projeteis.append(proj)
            self.tempo_ultimo_tiro = agora
    
    def attack_player(self, player):
        """Ataca o player se estiver dentro do alcance."""
        distancia = self.calcular_distancia(player)
        if distancia > self.distancia_ataque and not self.dead and not self.game.player.dead:
            self.realizar_ataque(player) 

    def realizar_ataque(self, player):
        """ Ataca o player caso esteja em contato """
        if self.can_attack():
            self.disparar_projétil(player)  # Atira no player
            self.attack_cooldown = pg.time.get_ticks()
            
    
    def update_projeteis(self):
        """Atualiza e remove projéteis fora do mapa"""
        for proj in self.projeteis[:]:
            proj.update()
            
            # Verifica se o projétil saiu dos limites do mapa
            if (not (0 <= proj.rect.x <= self.game.map.width and 
                    0 <= proj.rect.y <= self.game.map.height)):
                if proj in self.projeteis:  # Verificação extra antes de remover
                    self.projeteis.remove(proj)

            if proj.dead:
                if proj in self.projeteis:  # Verificação extra antes de remover
                    self.projeteis.remove(proj)

    def desenhar_projeteis(self, surface, camera_offset=None):
        if camera_offset is None:
            camera_offset = [0, 0]
        for proj in self.projeteis:
            proj.draw(surface, camera_offset)

      
class EsqueletoSoldado(Soldado):
    def __init__(self, game, sala, x, y):
        nome = "EsqueletoSoldado"
        
        vida_max = 120
        defesa = 3
        dano = 10
        velocidade_min = 90
        velocidade_max = 110
        
        velocidade = [90, 110]
        tamanho = [50, 60]

        
        super().__init__(game, nome, vida_max, defesa, dano, velocidade_min, velocidade_max, sala, x, y)

class OrcoSoldado(Soldado):
    def __init__(self, game, sala, x, y):
        nome = "OrcoSoldado"
        
        vida_max = 150 
        defesa = 6
        dano = 20
        velocidade_min = 65
        velocidade_max = 80
        
        velocidades = [65, 80]
        tamanho = [50, 60]
 
        
        super().__init__(game, nome, vida_max, defesa, dano, velocidade_min, velocidade_max, sala, x, y)
    

class EsqueletoArqueiro(Atirador):
    def __init__(self, game, sala, x, y):
        nome = "EsqueletoArqueiro"
        
        vida_max = 80 
        defesa = 1 
        dano = 7
        velocidade_min = 95
        velocidade_max = 115
        
        velocidades = [95, 115]
        tamanho = [50, 60]
 
        
        super().__init__(game, nome, vida_max, defesa, dano, velocidade_min, velocidade_max, sala, x, y)
    
CLASSES_INIMIGOS = {
"Esqueleto Soldado": EsqueletoSoldado,
"Esqueleto Arqueiro": EsqueletoArqueiro,
"Orco": OrcoSoldado,
"Boss": Boss
}  



        
