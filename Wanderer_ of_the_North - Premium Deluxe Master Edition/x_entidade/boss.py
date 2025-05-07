import pygame as pg
import random
import math
from x_entidade.entidade import load_animation_sprites

from settings import basic_entity_size, get_mask_rect
from x_entidade.projeteis import *
from settings import time_passed, cores
from x_entidade.inimigo import Inimigo

class Boss(Inimigo):
    def __init__(self, game, sala, x, y):
        nome = "Boss"
        tipo = "Especial"
        
        vida_max = 500
        defesa = 5
        velocidade_min = 60
        velocidade_max = 80
        
        super().__init__(game, nome, vida_max, defesa, velocidade_min, velocidade_max, sala, x, y, tipo)
        
        self.dano, self.dano_projetil = 40, 25
        self.tamanho_projetil = 10
        self.quantidade_balas = 1
        self.quantidade_ataques = 1
        self.bullet_speed = 6
        self.cor_projetil = cores["ciano"]
        
        self.projeteis = []
        self.tempo_ultimo_tiro = 0
        self.tempo_entre_tiros = 400  # em milissegundos
        self.distancia_ataque_fisico = 20
        self.distancia_ataque = 150
        
        # Ataque Especial 'Lança Infernal'
        self.ataque_especial_lanca_Cooldown = 0
        self.ataque_especial_lanca_timer = 3000
        
        # Ataque Especial 'Barragem de Fogo'
        self.ataque_especial_Barragem_Cooldown = 0
        self.ataque_especial_Barragem_timer = 6000
        
        self.ataque_especial_fuja_Cooldown = 0
        self.ataque_especial_fuja_timer = 9000 

        self.bersek_ativacao = 0
        self.bersek = False
        self.bersek_cooldown = 0
        self.bersek_timer = 10000

        # Redefine sprites com tamanho aumentado (1.5x maior)
        tamanho_boss = (int(basic_entity_size[0]*1.5), int(basic_entity_size[1]*1.75))
        self.animation_database = load_animation_sprites(self.path, size=tamanho_boss)

        # Atualiza imagem, rect, mask e hitbox com novo tamanho
        self.image = self.animation_database["IDLE"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = get_mask_rect(self.image, *self.rect.topleft)
        self.mask = pg.mask.from_surface(self.image)

        
        #velocidade = random.choice([90, 100, 110]) \\ possivel mudança para escolha de velocidades implementadas nas classes 
    def modo_bersek (self):
        quantidade_aumentada = 0
        distancia_diminuida = 0
        timer_diminuido = 0
        print('Modo Berserk Ativado')
        
        if quantidade_aumentada <= 2:
            if random.random() < 0.6:
                self.quantidade_ataques += 1
        
        if distancia_diminuida <= 2:
            distancia_diminuida += 1
            if random.random() < 0.5:
                self.distancia_ataque -= 50
                
        if timer_diminuido <= 1:
            timer_diminuido += 1
            
            if random.random() < 0.1:
                
                self.ataque_especial_lanca_timer /= 2 
                self.ataque_especial_Barragem_timer /= 2
                self.ataque_especial_fuja_timer /= 2
        
        if time_passed(self.bersek_cooldown, self.bersek_timer):
            self.bersek = False
            self.bersek_ativacao = 0
            
            #print('fim')
            
            if quantidade_aumentada != 0:
                self.quantidade_ataques = 1
            if distancia_diminuida != 0:
                self.distancia_ataque = 200
            if timer_diminuido != 0:
                self.ataque_especial_lanca_timer = 1500
                self.ataque_especial_Barragem_timer = 3000
                self.ataque_especial_fuja_timer = 5000 
        

    def mudar_instancia(self):
        """Muda a instância do inimigo com base na vida atual."""
        vida_ratio = self.vida / self.vida_max
        distancia = self.calcular_distancia(self.game.player)
        
        if self.bersek:
            self.perseguindo = True
            self.bersek_cooldown = pg.time.get_ticks()
            self.modo_bersek()

        else:
        
            if 0.7 < vida_ratio <= 0.9:
                self.fugindo = False
                self.perseguindo = True
            
            elif 0.3 < vida_ratio <= 0.7:
                # Alterna entre perseguir e fugir
                if not self.fugindo and pg.time.get_ticks() - self.fuga_timer > 5000:
                    if random.random() < 0.3:  # 30% de chance de fugir
                        self.fugindo = True

            elif vida_ratio <= 0.3:
                # Mais chance de fugir
                if not self.fugindo and pg.time.get_ticks() - self.fuga_timer > 1000:
                    if random.random() < 0.7:  # 70% de chance de fugir
                        self.fugindo = True
                    elif random.random() < 0.3: # 30% de chance de Berserkar
                        self.bersek = True
            else:
                self.fugindo = False
                self.perseguindo = distancia > self.distancia_ataque
            
        

    def disparar_projétil(self, target, quantidade_balas, spread_angle=0):
        """Dispara um ou mais projéteis em direção ao alvo"""
        agora = pg.time.get_ticks()
        if agora - self.tempo_ultimo_tiro >= self.tempo_entre_tiros:
            direcao_base = pg.math.Vector2(
                target.rect.centerx - self.rect.centerx,
                target.rect.centery - self.rect.centery
            )
            
            if direcao_base.length() == 0:
                direcao_base = pg.math.Vector2(1, 0)  # Direção padrão se estiver no mesmo ponto
            else:
                direcao_base = direcao_base.normalize()
            
            for i in range(quantidade_balas):
                # Calcula ângulo para projéteis múltiplos
                angle = -spread_angle/2 + (spread_angle/(quantidade_balas-1))*i if quantidade_balas > 1 else 0
                
                # Rotaciona a direção base
                direcao = direcao_base.rotate(angle) if angle != 0 else direcao_base
                
                proj = Projectile(
                    self.rect.centerx, 
                    self.rect.centery,
                    direcao,
                    speed=6,
                    owner=self,
                    damage=self.dano_projetil,
                    size=self.tamanho_projetil,
                    color=self.cor_projetil
                )
                self.projeteis.append(proj)
            
            self.tempo_ultimo_tiro = agora
            return True
        return False
    
    def attack_player(self, player):
        distancia = self.calcular_distancia(player)
        if not self.dead and not self.game.player.dead:
            if distancia <= self.distancia_ataque_fisico:
                self.realizar_ataque_fisico(player)
            elif distancia >= self.distancia_ataque:
                self.realizar_ataque_distancia(player)
                
    def realizar_ataque_fisico(self, player):
        """ Ataca o player caso esteja em contato """
        if self.hitbox.colliderect(player.hitbox) and self.can_attack():
            player.take_damage(self.dano)
            self.attack_cooldown = pg.time.get_ticks()

    def realizar_ataque_distancia(self, player):
        """ Ataca o player caso esteja em contato """
        if self.can_attack():
            # Ataque Berserk (executa apenas uma vez ao entrar em berserk)
            if self.bersek_ativacao == 0 and self.bersek:
                self.bersek_ativacao += 1
                self.ataque_especial_fuja_Cooldown = pg.time.get_ticks()
                self.disparar_projétil(player, quantidade_balas=15, spread_angle=360)
            
            # Verifica cada ataque especial independentemente
            if time_passed(self.ataque_especial_lanca_Cooldown, self.ataque_especial_lanca_timer):
                self.ataque_especial_lanca_Cooldown = pg.time.get_ticks()
                if random.random() < 0.3:
                    #print("Lanca Infernal")
                    for _ in range(self.quantidade_ataques + 1):
                        self.disparar_projétil(player, quantidade_balas=5, spread_angle=(15 if self.bersek else 60))
                else:
                    self.disparar_projétil(player, quantidade_balas=3, spread_angle=(10 if self.bersek else 40))
            
            if time_passed(self.ataque_especial_Barragem_Cooldown, self.ataque_especial_Barragem_timer):
                self.ataque_especial_Barragem_Cooldown = pg.time.get_ticks()
                if random.random() < 0.8:
                    #print("Barragem")
                    for _ in range(3):  # 3 rajadas rápidas
                        self.disparar_projétil(player, quantidade_balas=self.quantidade_ataques + 7, spread_angle=(180 if self.bersek else 360))
                else:
                    self.disparar_projétil(player, quantidade_balas=6, spread_angle=(180 if self.bersek else 360))
            
            if time_passed(self.ataque_especial_fuja_Cooldown, self.ataque_especial_fuja_timer):
                self.ataque_especial_fuja_Cooldown = pg.time.get_ticks()
                for _ in range(self.quantidade_ataques + 4):
                    #print("Fuja")
                    self.disparar_projétil(player, quantidade_balas=10, spread_angle=360)
            
            # Ataque normal (se nenhum especial estiver ativo)
            if all(not time_passed(cooldown, timer) for cooldown, timer in [
                (self.ataque_especial_lanca_Cooldown, self.ataque_especial_lanca_timer),
                (self.ataque_especial_Barragem_Cooldown, self.ataque_especial_Barragem_timer),
                (self.ataque_especial_fuja_Cooldown, self.ataque_especial_fuja_timer)
            ]):
                self.disparar_projétil(player, quantidade_balas=random.randint(1, 3), spread_angle=(45 if self.bersek else 15))
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
            