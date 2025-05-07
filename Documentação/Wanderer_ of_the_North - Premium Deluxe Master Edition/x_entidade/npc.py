# npc_class.py
import pygame
import pygame as pg
import random
import os
from settings import cores, WIDTH, HEIGHT, BASE_DIR

class Npc:
    def __init__(self, x, y, game, tamanho=(90, 90)):
        self.item_escolhido = False
        self.game = game
        self.frames = self._load_frames(tamanho)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Controle de animação
        self.anim_timer = 0
        self.anim_speed = 1000  # tempo em milissegundos para trocar de frame


        self.dialogo_ativo = False
        self.dialogo = None
        self.space_pressed = False

   
        # Sistema de interação
        self.alpha = 0
        self.interacted = False
        self.message = None
        self.message_time = 0
        self.font = pygame.font.Font(None, 28)
        
    def _load_frames(self, tamanho):
        """Carrega os frames do NPC"""
        frames = []
        try:
            # Lista de nomes de arquivos (sem o caminho completo)
            frame_names = [
                "spr_mago_1.png",
                "spr_mago_2.png",
                "spr_mago_3.png"
            ]
            
            # Caminho base para as imagens do NPC
            npc_path = os.path.join(BASE_DIR, "graphics", "npc")
            
            for name in frame_names:
                full_path = os.path.join(npc_path, name)
                #print(f"Tentando carregar imagem: {full_path}")  # Debug
                if os.path.exists(full_path):
                    img = pygame.image.load(full_path).convert_alpha()
                    frames.append(pygame.transform.scale(img, tamanho))
                else:
                    print(f"Arquivo não encontrado: {full_path}")
                    raise FileNotFoundError(f"Arquivo não encontrado: {full_path}")
                    
        except Exception as e:
            print(f"Erro ao carregar imagens do NPC: {e}")
            # Fallback - cria frames verdes
            for _ in range(4):
                surf = pygame.Surface(tamanho, pygame.SRCALPHA)
                surf.fill((0, 255, 0, 128))  # Verde semi-transparente
                frames.append(surf)
        return frames

    def update(self, dt):
        keys = pg.key.get_pressed()

        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

        if self.dialogo_ativo and self.dialogo:
            if keys[pg.K_SPACE]:
                if not self.space_pressed:
                    self.space_pressed = True
                    self.dialogo.avancar()
            else:
                self.space_pressed = False


        # Atualiza mensagem se existir
        if self.message and pygame.time.get_ticks() - self.message_time > 5000:
            self.message = None

    def draw(self, surface, camera_offset):
        """Desenha o NPC na tela"""
        pos = (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
        surface.blit(self.image, pos)
        
        # Desenha prompt de interação se jogador estiver próximo
        if self.is_player_near() and not self.interacted and not self.dialogo_ativo:

            self._draw_interaction_prompt(surface, camera_offset)
            
        # Desenha mensagem se existir
        if self.message:
            self._draw_message(surface)


    def is_player_near(self, distancia_minima=100):
        """Verifica se o jogador está perto o suficiente para interagir"""
        player = self.game.player
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return (dx ** 2 + dy ** 2) ** 0.5 <= distancia_minima

    def check_interaction(self, keys):
        if keys[pg.K_e]:
            if not self.dialogo_ativo:
                if self.item_escolhido:  # Se já escolheu item antes
                    mensagens = ["Já fez sua escolha, boa sorte campeão"]
                    self.dialogo = DialogueBox(self.game, mensagens, self)
                    self.dialogo_ativo = True
                else:  # Primeira interação
                    mensagens = [
                        "Olá, aventureiro!",
                        "Você parece cansado da jornada...",
                        "Tenho alguns itens para te ajudar.",
                        "Vamos negociar!"
                    ]
                    self.dialogo = DialogueBox(self.game, mensagens, self)
                    self.dialogo_ativo = True

    def _draw_interaction_prompt(self, surface, camera_offset):
        """Desenha o prompt de interação"""
        fonte = pygame.font.Font(None, 16)
        mensagem = fonte.render("Aperte 'E' para interagir", True, cores['branco'])
        
        # Ajusta a posição com o offset da câmera
        x = self.rect.x - camera_offset[0] - 50
        y = self.rect.y - camera_offset[1] - 30
        
        # Fundo semi-transparente
        fundo = pygame.Surface((140, 30), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, 150))
        
        surface.blit(fundo, (x, y))
        surface.blit(mensagem, (x + 10, y + 10))

    def _draw_message(self, surface):
        """Desenha a mensagem do NPC"""
        texto = self.font.render(self.message, True, cores['branco'])
        largura = texto.get_width() + 40
        altura = texto.get_height() + 20
        
        x = WIDTH // 2 - largura // 2
        y = HEIGHT // 2 - 100
        
        # Fundo da mensagem
        fundo = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(fundo, (0, 0, 0, 200), fundo.get_rect(), border_radius=10)
        
        surface.blit(fundo, (x, y))
        surface.blit(texto, (x + 20, y + 10))

    def _open_interaction_menu(self):
        """Abre o menu de interação com o NPC"""
        menu_aberto = True
        largura_menu = 500
        altura_menu = 230
        x_menu = (self.game.tela.get_width() - largura_menu) // 2
        y_menu = (self.game.tela.get_height() - altura_menu) // 2

        # Carrega imagens dos itens
        try:
            pocao_img = pygame.image.load(os.path.join(BASE_DIR, "graphics", "items", "pocao_velocidade.png")).convert_alpha()
            escudo_img = pygame.image.load(os.path.join(BASE_DIR, "graphics", "items", "escudo.png")).convert_alpha()
        except:
            # Fallback se as imagens não carregarem
            pocao_img = pygame.Surface((50, 50), pygame.SRCALPHA)
            pocao_img.fill((255, 0, 255, 128))
            escudo_img = pygame.Surface((50, 50), pygame.SRCALPHA)
            escudo_img.fill((0, 0, 255, 128))

        opcoes = [
            ("Poção Velocidade", pocao_img),
            ("Escudo Wanderer", escudo_img)
        ]
        
        for i in range(len(opcoes)):
            opcoes[i] = (opcoes[i][0], pygame.transform.scale(opcoes[i][1], (50, 50)))

        opcao_selecionada = 0
        fundo = self.game.tela.copy()

        while menu_aberto:
            self.game.tela.blit(fundo, (0, 0))
            sombra = pygame.Surface((largura_menu + 10, altura_menu + 10), pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 100))
            self.game.tela.blit(sombra, (x_menu - 5, y_menu - 5))

            pygame.draw.rect(self.game.tela, (30, 30, 30), (x_menu, y_menu, largura_menu, altura_menu), border_radius=15)
            titulo_menu = pygame.font.Font(None, 40).render("Escolha seu item:", True, (255, 255, 255))
            self.game.tela.blit(titulo_menu, (x_menu + 150, y_menu + 20))

            for i, (opcao, imagem) in enumerate(opcoes):
                cor = (255, 255, 255) if i == opcao_selecionada else (180, 180, 180)
                texto = pygame.font.Font(None, 40).render(opcao, True, cor)

                if i == opcao_selecionada:
                    pygame.draw.rect(self.game.tela, (255, 215, 0), 
                                (x_menu + 15, y_menu + 60 + i * 70, largura_menu - 30, 50), 
                                border_radius=10)

                self.game.tela.blit(imagem, (x_menu + 30, y_menu + 65 + i * 70))
                self.game.tela.blit(texto, (x_menu + 100, y_menu + 75 + i * 70))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        opcao_selecionada = (opcao_selecionada + 1) % len(opcoes)
                    elif event.key == pygame.K_w:
                        opcao_selecionada = (opcao_selecionada - 1) % len(opcoes)
                    elif event.key == pygame.K_RETURN:
                        item_escolhido = opcoes[opcao_selecionada][0]
                        
                        if item_escolhido == "Escudo Wanderer":
                            self.game.player.tem_escudo = True
                        elif item_escolhido == "Poção Velocidade":
                            self.game.player.pocao_magica = True
                            self.game.player.pocao_timer = pygame.time.get_ticks()
                        
                        self.item_escolhido = True  # Marca que já escolheu item
                        menu_aberto = False
                        self.dialogo = DialogueBox(self.game, ["Você é tudo que nos resta..."], self)
                        self.dialogo_ativo = True

class DialogueBox:
    def __init__(self, game, mensagens, npc):
        self.game = game
        self.npc = npc
        self.mensagens = mensagens
        self.index = 0
        self.ativa = True

        # Mantendo as cores e estilo medieval do design anterior
        self.cor_fundo = (20, 12, 28)          # Roxo escuro medieval
        self.cor_borda = (118, 66, 138)        # Roxo médio
        self.cor_texto = (230, 213, 184)       # Texto pergaminho
        self.cor_sombra = (10, 5, 15)          # Sombra escura
        self.radius = 8                         # Arredondamento da caixa

        # Usando a fonte PressStart2P (como na intro) mas mantendo o estilo
        font_path = os.path.join(BASE_DIR, "graphics", "fonts", "PressStart2P-Regular.ttf")
        self.fonte = pg.font.Font(font_path, 22)  # Aumentei para 22px (original era 18)
        
        # Dimensões originais (ajustadas só para o texto maior)
        self.largura = 1000
        self.altura = 150
        self.x = (WIDTH - self.largura) // 2
        self.y = HEIGHT - self.altura - 30

        # Imagem do NPC (igual à versão anterior)
        face_path = os.path.join(BASE_DIR, "graphics", "ui", "npc_face.png")
        try:
            self.face_image = pg.image.load(face_path).convert_alpha()
            # Moldura medieval (igual à anterior)
            moldura = pg.Surface((100, 100), pg.SRCALPHA)
            pg.draw.rect(moldura, (118, 66, 138, 200), moldura.get_rect(), border_radius=10)
            pg.draw.rect(moldura, (230, 213, 184, 255), moldura.get_rect(), 2, border_radius=10)
            self.face_image = pg.transform.scale(self.face_image, (90, 90))
            moldura.blit(self.face_image, (5, 5))
            self.face_image = moldura
        except:
            # Fallback visual (igual à anterior)
            self.face_image = pg.Surface((100, 100), pg.SRCALPHA)
            pg.draw.rect(self.face_image, (118, 66, 138), (0, 0, 100, 100), border_radius=10)
            texto_fallback = pg.font.Font(None, 20).render("NPC", True, (255, 255, 255))
            self.face_image.blit(texto_fallback, (35, 40))

        # Borda decorativa superior (igual à anterior)
        self.borda_decorativa = pg.Surface((self.largura, 20), pg.SRCALPHA)
        for i in range(0, self.largura, 40):
            pg.draw.polygon(self.borda_decorativa, (118, 66, 138), 
                            [(i, 20), (i+20, 0), (i+40, 20)])

    def avancar(self):
        self.index += 1
        if self.index >= len(self.mensagens):
            self.ativa = False
            if self.mensagens[-1] == "Vamos negociar!":  # Se for a última mensagem inicial
                self.npc._open_interaction_menu()  # Abre a loja
            else:  # Se for a mensagem pós-item
                self.npc.dialogo_ativo = False
                self.npc.dialogo = None

    def draw(self, surface):
        if not self.ativa:
            return

        # Desenho da caixa (idêntico ao anterior)
        # Sombra
        shadow_rect = pg.Rect(self.x + 5, self.y + 5, self.largura, self.altura)
        pg.draw.rect(surface, self.cor_sombra, shadow_rect, border_radius=self.radius)
        
        # Caixa principal
        box_rect = pg.Rect(self.x, self.y, self.largura, self.altura)
        pg.draw.rect(surface, self.cor_fundo, box_rect, border_radius=self.radius)
        pg.draw.rect(surface, self.cor_borda, box_rect, width=3, border_radius=self.radius)
        
        # Borda decorativa superior
        surface.blit(self.borda_decorativa, (self.x, self.y - 10))
        
        # Rosto do NPC
        surface.blit(self.face_image, (self.x + 20, self.y + 25))

        # Texto - agora com PressStart2P mas mantendo o estilo medieval
        texto = self.mensagens[self.index]
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        
        # Quebra de linha adaptada para a nova fonte
        for palavra in palavras:
            teste_linha = f"{linha_atual} {palavra}" if linha_atual else palavra
            if self.fonte.size(teste_linha)[0] < self.largura - 150:
                linha_atual = teste_linha
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
            
        # Renderização com nova fonte mas estilo visual igual
        for i, linha in enumerate(linhas):
            # Sombra do texto (posição levemente ajustada para a nova fonte)
            texto_sombra = self.fonte.render(linha, True, self.cor_sombra)
            surface.blit(texto_sombra, (self.x + 140 + 1, self.y + 40 + i*32 + 1))  # Ajuste fino no posicionamento
            
            # Texto principal
            texto_render = self.fonte.render(linha, True, self.cor_texto)
            surface.blit(texto_render, (self.x + 140, self.y + 40 + i*32))  # Espaçamento 32px entre linhas
        
        # Instrução para avançar (com estilo medieval mas fonte PressStart2P)
        instrucao = pg.font.Font(os.path.join(BASE_DIR, "graphics", "fonts", "PressStart2P-Regular.ttf"), 16).render(
            "Pressione ESPACO", True, (180, 160, 140))
        surface.blit(instrucao, (self.x + self.largura - 300, self.y + self.altura - 30))