
import pygame
import os
import sys
import cv2
import numpy as np

from pygame import mixer
from mapa import Map


def resetar_cursor():
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

def reproduzir_video_pygame(path_video, tela, tamanho=(1280, 720)):
    caminho_video = os.path.join(os.path.dirname(__file__), path_video)
    caminho_audio = os.path.join(os.path.dirname(__file__), "sounds", "audio_video_intro.mp3")

    cap = cv2.VideoCapture(caminho_video)
    if not cap.isOpened():
        print("Erro ao abrir o vídeo.")
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    clock = pygame.time.Clock()
    skip_requested = False

    # Configuração do áudio
    if pygame.mixer.get_init() and os.path.exists(caminho_audio):
        pygame.mixer.music.load(caminho_audio)
        pygame.mixer.music.play()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Processamento do frame (sem rotações ou flips desnecessários)
        frame = cv2.resize(frame, tamanho)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV usa BGR, PyGame usa RGB
        
        # Conversão direta para superfície PyGame (método mais robusto)
        frame_surface = pygame.image.frombuffer(
            frame.tobytes(), 
            tamanho, 
            'RGB'
        )

        # Renderização centralizada
        tela.blit(frame_surface, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    skip_requested = True
                    break

        if skip_requested:
            break

        clock.tick(fps if fps > 0 else 30)

    cap.release()
    pygame.mixer.music.stop()
    return skip_requested

def tela_inicial(tela,  mixer_ativo=True):
    if mixer_ativo and pygame.mixer.get_init() :
        pygame.mixer.music.stop()

    base_path = os.path.dirname(__file__)
    imagem_path = os.path.join(base_path, "graphics", "tela_inicial2.png")

    try:
        imagem_fundo = pygame.image.load(imagem_path)
        imagem_fundo = pygame.transform.scale(imagem_fundo, (1280, 750))
    except FileNotFoundError:
        print(f"Erro: imagem de fundo não encontrada em '{imagem_path}'")
        return False

    botao_rect = pygame.Rect((460, 590, 360, 60))
    clock = pygame.time.Clock()
    rodando = True

    pygame.event.clear()
    mouse_ja_pressionado = False

    while rodando:
        tela.blit(imagem_fundo, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        # Efeito de hover
        if botao_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            hover_surface = pygame.Surface((botao_rect.width, botao_rect.height), pygame.SRCALPHA)
            hover_surface.fill((255, 255, 255, 10))
            tela.blit(hover_surface, botao_rect.topleft)
        else:
            resetar_cursor()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_rect.collidepoint(evento.pos) and not mouse_ja_pressionado:
                    resetar_cursor()
                    return True

        pygame.display.flip()
        clock.tick(60)
    
    return False