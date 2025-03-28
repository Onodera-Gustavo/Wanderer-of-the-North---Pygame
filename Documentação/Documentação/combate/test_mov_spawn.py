import pygame as pg
import random
import sys
import math 
import time

# Inicializando o pygame
pg.init()

# Definindo o tamanho da tela
largura = 800
altura = 600

# Tela do game
tela = pg.display.set_mode((largura, altura))

# Cor do fundo da tela
cor = (0, 128, 0)

# Cor do retângulo
cor_retangulo1 = (0, 0, 0)  # Personagem
cor_retangulo2 = (0, 0, 255)  # Inimigos
cor_ataque = (255, 0, 0)  # Cor do ataque (vermelho)
cor_barra_poder = (0,0,255) # cor da amostra do nivel de poder

# Tela fundo do jogo
fundo_tela = pg.image.load("graphics\ground.png")

# Redimensiona a imagem para o tamanho da tela
fundo_tela = pg.transform.scale(fundo_tela, (largura, altura))

# Posição e dimensões do retângulo 1 (Personagem)
x1, y1 = 290, 270
largura_retangulo1, altura_retangulo1 = 30, 20

# Dimensão do retângulo 2 (Inimigos)
largura_retangulo2, altura_retangulo2 = 30, 20

# Velocidades dos personagens e inimigos
velocidade_personagem = 2
velocidade_inimigo = 0.5

# Vida do personagem principal
vida_personagem = 1000
poder_ataque = 50  # Poder de ataque do personagem
poder_maximo = 500 # limite do poder
poder_atual = 100 # poder inicial


# Lista de níveis dos inimigos
nivels_inimigos = [
    {"nivel": 1, "vida": 50, "dano": 5},
    {"nivel": 2, "vida": 100, "dano": 15},
    {"nivel": 3, "vida": 150, "dano": 25}
]

# Função para gerar inimigos aleatoriamente
def gerar_inimigos(quantidade):
    inimigos_gerados = []

    for _ in range(quantidade):
        inimigo = random.choice(nivels_inimigos)

        # Posição aleatória para o inimigo
        x_inimigo = random.randint(0, largura - 30)
        y_inimigo = random.randint(0, altura - 30)

        inimigos_gerados.append({
            "x": x_inimigo,
            "y": y_inimigo,
            "vida": inimigo["vida"],
            "dano": inimigo["dano"],
            "nivel": inimigo["nivel"],
            "ultimo_ataque": 0 # controla o tempo de ataque
        })

    return inimigos_gerados

# Gerar 10 inimigos aleatórios
inimigos_gerados = gerar_inimigos(random.randint(1, 3))

# função para desenhar barra de poder
def barra_de_poder():
    
    largura_barra = 200
    altura_barra = 20
    porcentagem_poder = poder_atual / poder_maximo
    pg.draw.rect(tela, (255, 255, 255), (10, 513, largura_barra, altura_barra), 2)  # Contorno branco
    pg.draw.rect(tela, cor_barra_poder, (10, 513, largura_barra * porcentagem_poder, altura_barra))  # Barra azul
    # Exibição do número do poder
    fonte_poder = pg.font.SysFont('times new roman', 20)
    texto_poder = fonte_poder.render(f'Poder: {int(poder_atual)}', True, (255, 255, 255))
    tela.blit(texto_poder, (20, 480))  # Posiciona o texto acima da barra

# Função de ataque do personagem
def atacar(inimigos, x1, y1, alcance_ataque):
    inimigos_atingidos = []
    # Checa se algum inimigo está dentro da área de ataque
    for inimigo in inimigos:
        # Calcular a distância entre o personagem e o inimigo
        distancia = math.sqrt((inimigo["x"] - x1) ** 2 + (inimigo["y"] - y1) ** 2)
        
        if distancia <= alcance_ataque:
            inimigos_atingidos.append(inimigo)
            # Subtrair a vida do inimigo com o poder de ataque
            inimigo["vida"] -= poder_ataque
            if inimigo["vida"] <= 0:
                inimigos.remove(inimigo)  # Remover inimigo da lista se ele for destruído
    return inimigos

# Loop do jogo
rodando = True
while rodando:
    # Preenche o fundo com a cor escolhida
    tela.fill(cor)

    # Desenhando o cenário
    tela.blit(fundo_tela, (0, 0))

    # Desenhando o retângulo do personagem
    pg.draw.rect(tela, cor_retangulo1, (x1, y1, largura_retangulo1, altura_retangulo1))
    
    # Desenhando os inimigos
    for inimigo in inimigos_gerados:
        pg.draw.rect(tela, cor_retangulo2, (inimigo["x"], inimigo["y"], largura_retangulo2, altura_retangulo2))

    # Movimentação do personagem
    teclas = pg.key.get_pressed()
    if teclas[pg.K_a]:
        x1 -= velocidade_personagem
    if teclas[pg.K_d]:
        x1 += velocidade_personagem
    if teclas[pg.K_w]:
        y1 -= velocidade_personagem
    if teclas[pg.K_s]:
        y1 += velocidade_personagem
        
    # Checa se a tecla "Espaço" foi pressionada para atacar
    if teclas[pg.K_SPACE]:
        inimigos_gerados = atacar(inimigos_gerados, x1, y1, 50)  # 50 é o alcance do ataqueaa

    # Impedir que o personagem saia da tela
    if x1 < 0:
        x1 = 0
    if x1 + largura_retangulo1 > largura:
        x1 = largura - largura_retangulo1
    if y1 < 0:
        y1 = 0
    if y1 + altura_retangulo1 > altura:
        y1 = altura - altura_retangulo1

    tempo_atual = time.time()
    # Movimentação dos inimigos (seguindo o personagem)
    for inimigo in inimigos_gerados:
        if inimigo["x"] < x1:
            inimigo["x"] += velocidade_inimigo
        elif inimigo["x"] > x1:
            inimigo["x"] -= velocidade_inimigo

        if inimigo["y"] < y1:
            inimigo["y"] += velocidade_inimigo
        elif inimigo["y"] > y1:
            inimigo["y"] -= velocidade_inimigo

    # verifica se  está perto o suficiente para atacar
    distancia_inimigo = math.sqrt((inimigo["x"] - x1) ** 2 + (inimigo["y"] - y1) ** 2)
    if distancia_inimigo <= 30  and (tempo_atual - inimigo["ultimo_ataque"]) > 1.5:
        vida_personagem -= inimigo["dano"]
        inimigo["ultimo_ataque"] = tempo_atual
        

    if inimigos_gerados == []:
        inimigos_gerados = gerar_inimigos(random.randint(1, 30))

    

    # Exibição da vida do personagem na tela
    fonte = pg.font.SysFont('times new roman', 30)
    texto_vida_personagem = fonte.render(f'Vida: {vida_personagem}', True, (255, 255, 255))
    tela.blit(texto_vida_personagem, (10, 10))

     # desenhar barra poder
    barra_de_poder()

    # Atualiza a tela do jogo
    pg.display.update()

    # Verifica eventos (como sair do jogo)
    for evento in pg.event.get():
        if evento.type == pg.QUIT:
            rodando = False

    # Game over quando a vida do personagem chega a zero
    if vida_personagem <= 0:
        print('GAME OVER!!!')
        rodando = False

# Finaliza o Pygame
pg.quit()
sys.exit()
