import pygame
from pytmx import load_pygame, TiledTileLayer
from inimigo import *

class Map:
    def __init__(self,tmx_file):
        
        #Carrega o arquivo tmx
        self.tmx_data = load_pygame(tmx_file)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        

    def draw(self, tela):

        #superficie onde o mapa será desenhado

        # offset_x, offset_y = camera_offset

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        tela.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight )) 

    def Get_size(self):

        #Retorna as dimensões do mapa
        return self.width, self.height
    

class Sala:
    def __init__(self, nivel):
        self.nivel = nivel
        self.inimigos = self.gerar_inimigos()

    def gerar_inimigos(self):
        inimigos_gerados = []
        quantidade = random.randint(5, 10)  # Define a quantidade de inimigos na sala
        
        for _ in range(quantidade):
            # Filtra os inimigos disponíveis para o nível atual
            inimigos_disponiveis = [nome for nome, classe in CLASSES_INIMIGOS.items() if self.nivel_in_range(nome)]
            if not inimigos_disponiveis:
                continue
            
            inimigo_nome = random.choice(inimigos_disponiveis)
            inimigo_classe = CLASSES_INIMIGOS[inimigo_nome]
            
            x_inimigo = random.randint(0, WIDTH - 30)
            y_inimigo = random.randint(0, HEIGHT - 30)
            
            inimigo = inimigo_classe(x_inimigo, y_inimigo, self.nivel)
            inimigos_gerados.append(inimigo)
        
        return inimigos_gerados
    
    def nivel_in_range(self, inimigo_nome):
        niveis = {
            "Esqueleto Soldado": (1, 3),
            "Demônio": (5, 7),
            "Aberração": (6, 7),
            "Orco": (3, 7),
            "Goblin": (1, 3),
            "Morcego Gigante": (1, 3),
            "Esqueleto Arqueiro": (1, 3),
            "Cultista Iniciado": (3, 5),
            "Cultista Sacerdote": (4, 6),
            "Cultista Diácono": (6, 7)
        }
        
        if inimigo_nome in niveis:
            min_nivel, max_nivel = niveis[inimigo_nome]
            return min_nivel <= self.nivel <= max_nivel
        return False
