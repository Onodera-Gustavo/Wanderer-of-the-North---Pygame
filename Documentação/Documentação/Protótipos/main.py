import pygame as pg
import random

# inicializando o pygame
pg.init()

# definindo o tamanho da tela
largura = 800
altura = 600

# tela do game
tela = pg.display.set_mode((largura, altura))

# mudando cor da tela do jogo
cor = (0,128,0)

# cor do retangulo
cor_retangulo1 = (0,0,0)
cor_retangulo2 = (0,0,255)


# posição e dimensão do retangulo 1
x1, y1 = 290, 270
largura_retangulo1, altura_retangulo1 = 150, 40

# posição e dimensão do retangulo 2
x2, y2 = 0, 0
largura_retangulo2, altura_retangulo2 = 150, 40

# velocidades dos personagens e inimigos
velocidade_personagem = 2
velocidade_inimigo = 0.5

# vida personagem principal
vida_personagem = 1000

# loop do jogo
rodando = True

while rodando:
     # Preenche o fundo com a cor escolhida
    tela.fill(cor)
    
    # desenhando o retangulo na tela
    pg.draw.rect(tela, cor_retangulo1, (x1, y1, largura_retangulo1, altura_retangulo1))
    pg.draw.rect(tela, cor_retangulo2, (x2, y2, largura_retangulo2, altura_retangulo2))

    # fazendo os retangulos se moverem 
    teclas = pg.key.get_pressed()

    if teclas[pg.K_a]:
        x1-= velocidade_personagem
    if teclas[pg.K_d]:
        x1+= velocidade_personagem
    if teclas[pg.K_w]:
        y1-= velocidade_personagem
    if teclas[pg.K_s]:
        y1+= velocidade_personagem 
    
    # retangulo 2 se movendo atras do retangulo 1
    if x2 < x1:
        x2+= velocidade_inimigo
    elif x2 > x1:
        x2 -= velocidade_inimigo

    if y2 < y1:
        y2 += velocidade_inimigo
    elif y2 > y1:
        y2 -= velocidade_inimigo
    
    # impedir que os retangulos saiam da tela  
    if x1 < 0:
        x1 = 0
    if x1 + largura_retangulo1 > largura:
        x1 = largura - largura_retangulo1
    if y1 < 0:
        y1 = 0
    if y1 + altura_retangulo1 > altura:
        y1 = altura - altura_retangulo1 

    if x2 < 0:
        x2 = 0
    if x2 + altura_retangulo2 > altura:
        x2 = altura - altura_retangulo2
    if x2 + largura_retangulo2 > largura:
        x2 = largura - largura_retangulo2

    # colisão dos retangulos
    ret_1 = pg.draw.rect(tela, cor_retangulo1, (x1, y1, largura_retangulo1, altura_retangulo1))
    ret_2 = pg.draw.rect(tela, cor_retangulo2, (x2, y2, largura_retangulo2, altura_retangulo2))
     
    if ret_1.colliderect(ret_2):
        vida_personagem -= 1

    # exibição da vida do personagem na tela
    fonte = pg.font.SysFont('times new roman', 30)
    texto_vida_personagem = fonte.render(f'vida: {vida_personagem}', True, (255,255,255))
    tela.blit(texto_vida_personagem,(10,10))

    


    # atualiza a tela do jogo
    pg.display.update()
      
    for evento in pg.event.get():
        if evento.type == pg.QUIT:
            rodando = False

    # game over !!!
    if vida_personagem <= 0:
        print('GAME OVER')
        rodando = False



# encerramento do jogo
pg.quit() 

