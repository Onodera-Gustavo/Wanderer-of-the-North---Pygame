import pygame as pg
from pytmx import load_pygame, TiledTileLayer
from inimigo import *

class Map:
    def __init__(self, tmx_file):
        # Carrega o mapa TMX
        self.tmx_data = load_pygame(tmx_file)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

    def draw(self, tela):
        """Desenha o mapa na tela."""
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        tela.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

    def Get_size(self):
        """Retorna as dimensões do mapa."""
        return self.width, self.height

class Sala:
    def __init__(self, game, nivel):
        self.game = game
        self.nivel = nivel
        self.inimigos = self.gerar_inimigos()
        self.tempo_onda = 0  # Tempo para gerar nova onda de inimigos

    def gerar_inimigos(self):
        """Gera inimigos de acordo com o nível."""
        inimigos_gerados = []
        quantidade = random.randint(5, 10) 

        sala_x_min, sala_y_min = 100, 100
        sala_x_max, sala_y_max = WIDTH - 100, HEIGHT - 100

        for _ in range(quantidade):
            inimigos_disponiveis = [nome for nome in CLASSES_INIMIGOS.keys() if self.nivel_in_range(nome)]
            if not inimigos_disponiveis:
                continue

            inimigo_nome = random.choice(inimigos_disponiveis)
            inimigo_classe = CLASSES_INIMIGOS[inimigo_nome]

            x_inimigo = random.randint(sala_x_min, sala_x_max)
            y_inimigo = random.randint(sala_y_min, sala_y_max)

            inimigo = inimigo_classe(self.game, self, x_inimigo, y_inimigo)
            inimigos_gerados.append(inimigo)
        return inimigos_gerados
        
    def nova_onda(self):
        """Gera uma nova onda de inimigos se o tempo passou e não há inimigos vivos."""
        inimigos_vivos = [i for i in self.inimigos if not i.dead]

        if not inimigos_vivos and self.Tempo():
            novos_inimigos = self.gerar_inimigos()
            self.inimigos.extend(novos_inimigos)


    def nivel_in_range(self, inimigo_nome):
        """Define quais inimigos aparecem em cada fase."""
        niveis = {
            "Esqueleto Soldado": (1, 3),
            "Orco": (1, 7),
            "Esqueleto Arqueiro": (1, 3)
        }
        return niveis.get(inimigo_nome, (0, 0))[0] <= self.nivel <= niveis[inimigo_nome][1]
