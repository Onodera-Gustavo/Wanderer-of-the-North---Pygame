import pygame
from mapa import Map
from player import Player, Sword
from settings import *


class Game:
    def __init__(self):
        # Inicializa o pygame
        pygame.init()
        self.tela = pygame.display.set_mode((1280, 735))
        pygame.display.set_caption('Jogo')

        # Carrega o mapa
        self.mapa = Map(r'Sistema\MAP(1) - COMPLET.tmx') #Mude o caminho caso esteja na sua maquina

        # Grupo de sprites
        self.sprites = pygame.sprite.Group()
        
        # Criar o jogador
        
        
        self.player = Player((400, 300), self.sprites)
        self.sword = Sword(self.player)

        self.clock = pygame.time.Clock()  # Linha para criar o relógio

        #Obter as dimensões do mapa
        # self.map_width, self.map_height = self.mapa.Get_size()
        # self.camera_offset = [0, 0]

    def update(self):
        """Atualiza a lógica do jogo."""
        self.sprites.update()  # Atualiza o player e outros sprites
        # self.calculate_camera_offset() # Atualiza o deslocamento da camera
        self.sword.update()  # Atualiza a espada do jogador

    def draw(self):

        """Desenha os elementos na tela."""
        self.tela.fill((0, 0, 0))  # Limpa a tela (preto)
        self.mapa.draw(self.tela)  # Desenha o mapa
        
        
        #desenhar sprite ajustados pela camera
        for sprite in self.sprites:
            self.tela.blit(sprite.image,(sprite.rect.x , sprite.rect.y ))

        self.sword.draw(screen)
            

        pygame.display.flip()  # Atualiza a tela

    def run(self):
        """Loop principal do jogo."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.sword.attack()

            self.update()  # Atualiza a lógica do jogo
            self.draw()  # Desenha os elementos na tela
            self.clock.tick(60)  # Limita o FPS para 60


    # def calculate_camera_offset(self):
    #     half_width = self.tela.get_width() // 2
    #     half_height = self.tela.get_height() // 2

    #     #Centraliza o jogador na tela
    #     offset_x = self.player.rect.centerx - half_width
    #     offset_y = self.player.rect.centery - half_height   

    #     #Limitar a camera para não passar das bordas do mapa
    #     offset_x = max(0, min(offset_x, self.map_width - self.tela.get_width()))
    #     offset_y = max(0, min(offset_y, self.map_height - self.tela.get_height()))

    #     self.camera_offset = [offset_x, offset_y]#Atualiza a posição da camera

if __name__ == "__main__":
    jogo = Game()  # Cria uma instância do jogo
    jogo.run()  # Inicia o loop do jogo
