import pygame
from pytmx import load_pygame, TiledTileLayer

class Map:
    def __init__(self,tmx_file):
        
        #Carrega o arquivo tmx
        self.tmx_data = load_pygame(tmx_file)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        

    def draw(self, tela, camera_offset):

        #superficie onde o mapa será desenhado

        offset_x, offset_y = camera_offset

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        tela.blit(tile, (x * self.tmx_data.tilewidth - offset_x, y * self.tmx_data.tileheight - offset_y ))

    def Get_size(self):

        #Retorna as dimensões do mapa
        return self.width, self.height