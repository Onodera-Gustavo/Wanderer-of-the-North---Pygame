import pygame 
import os

from mapa import Map, Sala
from player import Player, Sword
from settings import *
from inimigo import *

class Game:
    def __init__(self):
        # Inicializa o pygame
        pygame.init()
        self.tela = pygame.display.set_mode((1280, 735))
        pygame.display.set_caption('Jogo')
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # Carrega o mapa
        self.mapa = Map(BASE_DIR +'\mapa(1).tmx') # Mude o caminho se necessário

        # Grupo de sprites
        self.sprites = pygame.sprite.Group()
        
        # Criar o jogador
        self.player = Player((400, 300), self.sprites)
        self.sword = Sword(self.player)

        self.clock = pygame.time.Clock()  # Relógio para FPS

        # Criar a sala e gerar inimigos com base na fase
        self.nivel = 1  # Definir o nível inicial
        self.sala = Sala(self, self.nivel)


    def update(self):
        """Atualiza a lógica do jogo."""
        self.sprites.update()  # Atualiza o player e outros sprites
        self.sword.update()  # Atualiza a espada do jogador

        # Atualizar inimigos
        for inimigo in self.sala.inimigos:
            inimigo.basic_update()

    def draw(self):
        """Desenha os elementos na tela."""
        self.tela.fill((0, 0, 0))  # Limpa a tela (preto)
        self.mapa.draw(self.tela)  # Desenha o mapa
        
        # Desenhar sprites ajustados pela câmera
        for sprite in self.sprites:
            self.tela.blit(sprite.image, (sprite.rect.x, sprite.rect.y))
            
        # Desenhar inimigos
        for inimigo in self.sala.inimigos:
            inimigo.update()
            inimigo.draw(self.tela)
            
            if self.sword.attacking and self.sword.check_collision([inimigo]):  # Só dá dano uma vez por ataque
                inimigo.take_damage(20)

        self.sword.draw(self.tela)

        pygame.display.flip()  # Atualiza a tela

    def run(self):
        """Loop principal do jogo."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.sword.attack()

            


            self.update()  # Atualiza a lógica do jogo
            self.draw()  # Desenha os elementos na tela
            self.clock.tick(60)  # Limita o FPS para 60

if __name__ == "__main__":
    jogo = Game()  # Cria uma instância do jogo
    jogo.run()  # Inicia o loop do jogo
