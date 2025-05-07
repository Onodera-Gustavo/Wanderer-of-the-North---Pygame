import pygame
import random
import time
from x_entidade.ordenacao import CLASSES_INIMIGOS, EsqueletoSoldado, EsqueletoArqueiro, OrcoSoldado
from settings import time_passed

class Sala:
    def __init__(self, game):
        self.game = game
        self.nivel = 1
        self._definir_limites()
        self.inimigos = self.gerar_inimigos()
        self.tempo_ultima_geracao = time.time()
        self.sala_limpa = len(self.inimigos) == 0
        
        # Define limites
        self.sala_x_min = self.limites['x_min']
        self.sala_y_min = self.limites['y_min']
        self.sala_x_max = self.limites['x_max']
        self.sala_y_max = self.limites['y_max']

    def _definir_limites(self):
        margin = 100
        self.limites = {
            'x_min': margin,
            'y_min': margin,
            'x_max': self.game.map.width - margin,
            'y_max': self.game.map.height - margin
        }
        self.sala_x_min = margin
        self.sala_y_min = margin
        self.sala_x_max = self.game.map.width - margin
        self.sala_y_max = self.game.map.height - margin

    # def gerar_inimigos(self):
    #     inimigos = []
        
    #     # Verifica se é o mapa 7 (boss map)
    #     if self.game.current_map.lower() == "map7":
    #         # Gera apenas 1 boss no centro da sala
    #         x = self.game.map.width // 2
    #         y = self.game.map.height // 2
    #         inimigo = CLASSES_INIMIGOS["Boss"](self.game, self, x, y)
    #         inimigos.append(inimigo)
    #         return inimigos
        
    #     # Geração normal de inimigos para outros mapas
    #     quantidade = random.randint(5, 10)
        
    #     for _ in range(quantidade):
    #         tipo = self._escolher_tipo_inimigo()
    #         if not tipo:
    #             continue
                
    #         x, y = self._gerar_posicao_valida()
            
    #         try:
    #             inimigo = CLASSES_INIMIGOS[tipo](self.game, self, x, y)
    #             inimigos.append(inimigo)
    #         except Exception as e:
    #             print(f"Erro ao criar inimigo {tipo}: {e}")

    #     return inimigos

    def _gerar_posicao_valida(self):
        """Gera posições válidas evitando spawn perto do jogador"""
        while True:
            x = random.randint(self.limites['x_min'], self.limites['x_max'])
            y = random.randint(self.limites['y_min'], self.limites['y_max'])
            
            distancia = pygame.math.Vector2(
                x - self.game.player.rect.x,
                y - self.game.player.rect.y
            ).length()
            
            if distancia >= 200:
                return x, y

    def _escolher_tipo_inimigo(self):
        mapa_atual = self.game.current_map.lower()

        # No mapa 7, só pode ser Boss (já tratado em gerar_inimigos)
        if mapa_atual == "map7":
            return None

        # Filtra inimigos permitidos para este mapa
        disponiveis = [
            nome for nome in CLASSES_INIMIGOS.keys() 
            if self._mapa_valido(nome, mapa_atual)
        ]
        
        return random.choice(disponiveis) if disponiveis else None

    def _mapa_valido(self, nome_inimigo, mapa):
        mapas_por_inimigo = {
            "Esqueleto Soldado": ["map1", "map3", "map4","map5"],
            "Esqueleto Arqueiro": ["map1", "map3", "map4"],
            "Orco": ["map1", "map3", "map5"],
            "Boss": ["map7"]  # Boss só aparece no mapa 7
        }
        return mapa in mapas_por_inimigo.get(nome_inimigo, [])

    def update(self):
        # Remove apenas inimigos que completaram a animação de morte
        self.inimigos = [inimigo for inimigo in self.inimigos 
                        if not inimigo.dead or 
                        (inimigo.dead and not inimigo.animation_complete)]
        
        sala_limpa_agora = len(self.inimigos) == 0
        
        if sala_limpa_agora and not self.sala_limpa:
            self.sala_limpa = True
            self.tempo_ultima_geracao = time.time()
        elif not sala_limpa_agora:
            self.sala_limpa = False

    def _todos_inimigos_mortos(self):
        return all(inimigo.dead and inimigo.animation_complete for inimigo in self.inimigos)
    
    def gerar_inimigos(self):
        inimigos = []
        
        # Verifica se é o mapa 7 (boss map)
        if self.game.current_map.lower() == "map7":
            # Gera apenas 1 boss no centro da sala
            x = self.game.map.width // 2
            y = self.game.map.height // 2
            
            # DEBUG: Verifica se a classe Boss existe
            if "Boss" in CLASSES_INIMIGOS:
                print("Criando boss...")
                inimigo = CLASSES_INIMIGOS["Boss"](self.game, self, x, y)
                inimigos.append(inimigo)
                print("Boss criado com sucesso!")
            else:
                print("Erro: Classe Boss não encontrada em CLASSES_INIMIGOS")
        
            return inimigos
        
        # Para outros inimigos, geração rápida
        quantidade = random.randint(5, 10)
        positions = [self._gerar_posicao_valida() for _ in range(quantidade)]
        
        for pos, tipo in zip(positions, [self._escolher_tipo_inimigo() for _ in range(quantidade)]):
            if tipo:
                x, y = pos
                try:
                    inimigo = CLASSES_INIMIGOS[tipo](self.game, self, x, y)
                    inimigos.append(inimigo)
                except Exception as e:
                    print(f"Erro ao criar inimigo {tipo}: {e}")
        
        return inimigos