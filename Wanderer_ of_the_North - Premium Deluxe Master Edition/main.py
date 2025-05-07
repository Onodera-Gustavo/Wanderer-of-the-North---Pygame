import pygame
import sys
from ffpyplayer.player import MediaPlayer
import cv2
from window import tela_inicial, reproduzir_video_pygame, resetar_cursor
import os
from x_entidade.boss import Boss
from settings import WIDTH, HEIGHT
from mapa import Map
from sala import Sala
from x_entidade.player import Player, Sword
from x_entidade.npc import Npc
from pygame import mixer
from pytmx import TiledTileLayer

BOSS_MUSIC_EVENT = pygame.USEREVENT + 2

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.tela = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Jogo Dungeon')

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.musicas = {
            "map1": os.path.join(base_dir, "sounds", "mountain-music.mp3"),
            "map2": os.path.join(base_dir, "sounds", "mountain-music.mp3"),
            "map3": os.path.join(base_dir, "sounds", "dungeon-music.mp3"),
            "map4": os.path.join(base_dir, "sounds", "dungeon-music.mp3"),
            "map5": os.path.join(base_dir, "sounds", "dungeon-music.mp3"),
            "map6": os.path.join(base_dir, "sounds", "dungeon-music.mp3"),
            "boss_music": os.path.join(base_dir, "sounds", "boss_music.mp3"),
        }

        self.boss_death_video_path = os.path.join(base_dir, "graphics", "intro_epica.mp4")
        self.faint_music_path = os.path.join(base_dir, "sounds", "faint.mp3")
        self.epic_sequence_active = False
        self.faint_music_playing = False
        self.original_damage = 200  # Guarda o dano original


        self.musica_atual = None
        self.volume = 0.5  # Volume padrão (0.0 a 1.0)

        self.primeira_vez = True  # Adiciona esta flag
        self.camera_offset = [0, 0]
        
        # Chama apenas a tela inicial aqui
        self.tela_inicial_ativa = True
        self.game_over = False
        
        # O resto da inicialização será feita depois do start
        self.inicializado = False
        self.boss_music_playing = False 
        self.boss_intro_played = False


        self.boss_music_playing = False 
        self.boss_intro_played = False
        self.boss_video_path = os.path.join(base_dir, "graphics", "intro_epica.mp4")  # Modificado para caminho direto
            
        
    def show_initial_screens(self):
        # Mostra tela inicial e verifica se clicou em START
        if tela_inicial(self.tela):
            self.tela_inicial_ativa = False
            # Só mostra intro na primeira vez
            if self.primeira_vez:
                # Pausa a música se estiver tocando
                mixer_was_playing = pygame.mixer.music.get_busy()
                if mixer_was_playing:
                    pygame.mixer.music.pause()
                
                # Reproduz o vídeo com possibilidade de skip
                reproduzir_video_pygame("graphics/videointro.mp4", self.tela)
                
                # Restaura a música se estava tocando antes
                if mixer_was_playing:
                    pygame.mixer.music.unpause()
                
                self.primeira_vez = False
            
            # Agora sim inicializa o jogo
            self._inicializar_jogo()
            # Toca a música do mapa inicial
            self.play_music(self.current_map)
            return True
        return False

    @staticmethod
    def play_video_with_audio_and_skip(video_path, screen):
        # Inicializa fonte do pygame explicitamente

        if not pygame.font.get_init():
            pygame.font.init()

        cap = cv2.VideoCapture(video_path) 
        player = MediaPlayer(video_path)
        clock = pygame.time.Clock()
        skip = False

        # Fonte e texto
        font_path = os.path.join("graphics", "fonts", "PressStart2P-Regular.ttf")
        font = pygame.font.Font(font_path, 16       )  # Você pode ajustar o tamanho
        texto = font.render("Aperte ENTER para pular", True, (255, 255, 255))

        while cap.isOpened():
            ret, frame = cap.read()
            audio_frame, val = player.get_frame()
            if val == 'eof':
                break
            if audio_frame:
                img, t = audio_frame


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    player.close_player()
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    player.toggle_pause()
                    skip = True

            if skip or not ret:
                break

            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                frame_surface = pygame.transform.scale(frame_surface, screen.get_size())
                screen.blit(frame_surface, (0, 0))

            # 🔁 Sempre desenha o texto por cima, mesmo que frame seja None
            screen.blit(texto, (screen.get_width() - texto.get_width() - 20, 20))

            pygame.display.flip()
            clock.tick(30)

        cap.release()
        player.close_player()


    def show_initial_screens(self):
        if tela_inicial(self.tela):
            self.tela_inicial_ativa = False
            
            if self.primeira_vez:
                # Pausa música atual (se estiver tocando)
                mixer_was_playing = mixer.music.get_busy()
                if mixer_was_playing:
                    mixer.music.pause()

                # Reproduz vídeo (com skip por Enter)
                skip = Game.play_video_with_audio_and_skip("graphics/videointro.mp4", self.tela)


                # Restaura música (se estava tocando antes)
                if mixer_was_playing:
                    mixer.music.unpause()

                self.primeira_vez = False

            # Inicializa o jogo
            self._inicializar_jogo()
            self.play_music(self.current_map)
            return True
        return False

    def _inicializar_jogo(self):
        """Inicializa todos os componentes do jogo"""
        if self.inicializado:
            return
            
        # Sistema de mapas
        self.maps = {
            "map1": Map(r'graphics\Maps\MAP(1) - COMPLET.tmx'),
            "map2": Map(r'graphics\Maps\Map(2) - COMPLET.tmx'),
            "map3": Map(r'graphics\Maps\Entrada.tmx'),
            "map4": Map(r'graphics\Maps\Cozinha.tmx'),
            "map5": Map(r'graphics\Maps\Dormitório.tmx'),
            "map6": Map(r'graphics\Maps\Salao-Principal.tmx'),
            "map7": Map(r'graphics\Maps\MAP(4) - COMPLET.tmx')
        }
        self.current_map = "map1"
        self.map = self.maps[self.current_map]
        
        # Jogador e armas
        spawn_x = self.map.width // 2
        spawn_y = self.map.height // 2
        self.player = Player((spawn_x, spawn_y), self)
        self.sword = Sword(self.player)
        
        # Restante da inicialização...
        self.sala = Sala(self)
        self.npc = None
        self._setup_npc()
        
        self.transition_cooldown = 0
        self.transition_data = None
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.transition_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        self.inicializado = True

            
    def show_game_over_screen(self):
        base_path = os.path.dirname(__file__)
        imagem_path = os.path.join(base_path, "graphics", "img_game_over5.png")

        try:
            imagem_fundo = pygame.image.load(imagem_path)
            imagem_fundo = pygame.transform.scale(imagem_fundo, (1280, 750))
        except FileNotFoundError:
            print(f"Erro: imagem de game over não encontrada em '{imagem_path}'")
            return

        botao_rect = pygame.Rect((460, 590, 360, 60))
        clock = pygame.time.Clock()
        rodando = True

        while rodando:
            self.tela.blit(imagem_fundo, (0, 0))
            mouse_pos = pygame.mouse.get_pos()

            # Efeito de hover
            if botao_rect.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                hover_surface = pygame.Surface((botao_rect.width, botao_rect.height), pygame.SRCALPHA)
                hover_surface.fill((255, 255, 255, 10))
                self.tela.blit(hover_surface, botao_rect.topleft)
            else:
                resetar_cursor()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if botao_rect.collidepoint(evento.pos):
                        # Reinicia o jogo sem a intro
                        self.__init__()
                        self.primeira_vez = False  # Mantém como False
                        self.tela_inicial_ativa = True  # Volta para tela inicial
                        return

                pygame.display.flip()
                clock.tick(60)  # Mover o clock.tick(60) para fora do loop  

#added now
        
    def calculate_camera_offset(self):
        # Mantenha o jogador no centro da tela
        target_x = self.player.rect.centerx - WIDTH // 2
        target_y = self.player.rect.centery - HEIGHT // 2
        
        # Limita aos bordos do mapa, garantindo que a câmera não ultrapasse os limites
        # mas permitindo que mostre todo o mapa se ele for menor que a tela
        max_x_offset = max(0, self.map.width - WIDTH)
        max_y_offset = max(0, self.map.height - HEIGHT)
        
        self.camera_offset[0] = max(0, min(target_x, max_x_offset))
        self.camera_offset[1] = max(0, min(target_y, max_y_offset))
    
    def _setup_npc(self):
        """Configura o NPC apenas para o map2"""
        #print(f"Configurando NPC para o mapa {self.current_map}")  # Debug
        self.npc = None
        
        if self.current_map == "map2":
            #print("Criando NPC para o map2")  # Debug
            npc_x = self.map.width // 2 - 200
            npc_y = self.map.height // 2 + 75
            self.npc = Npc(npc_x, npc_y, self)
            #print(f"NPC criado na posição ({npc_x}, {npc_y})")  # Debug

    def draw(self):
        self.tela.fill((0, 0, 0))  # Limpa a tela principal

        if hasattr(self, 'transition_data') and self.transition_data is not None:
            self._draw_transition()
        else:
            self._draw_game_elements()

        # 🔥 Aplica filtro vermelho na sala do boss
        if self.current_map == "map7":
            filtro = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            filtro.fill((255, 0, 0, 60))  # Aumente o alpha para intensificar
            self.tela.blit(filtro, (0, 0))

        pygame.display.flip()

    def _draw_boss_health(self, boss):
        # Barra de vida no topo da tela
        barra_largura = 800
        barra_altura = 30
        barra_x = (WIDTH - barra_largura) // 2
        barra_y = 40

        # Proporção de vida
        vida_ratio = boss.vida / boss.vida_max
        barra_vermelha = pygame.Rect(barra_x, barra_y, barra_largura, barra_altura)
        barra_verde = pygame.Rect(barra_x, barra_y, int(barra_largura * vida_ratio), barra_altura)

        pygame.draw.rect(self.tela, (255, 0, 0), barra_vermelha)
        pygame.draw.rect(self.tela, (0, 255, 0), barra_verde)
        pygame.draw.rect(self.tela, (0, 0, 0), barra_vermelha, 3)

        # Texto do nome do boss
        fonte_path = os.path.join("graphics", "fonts", "PressStart2P-Regular.ttf")
        fonte = pygame.font.Font(fonte_path, 18)
        texto = fonte.render("Skull, o devorador de almas", True, (255, 255, 255))
        texto_rect = texto.get_rect(center=(WIDTH // 2, barra_y - 20))
        self.tela.blit(texto, texto_rect)



    def _draw_game_elements(self):
        self.tela.fill((0, 0, 0))  # Limpa a tela principal
        
        # 1. Desenha o mapa de fundo (camadas base)
        self.map.draw_background(self.tela, self.camera_offset)
        
        # 2. Desenha NPC se existir (por baixo de player e inimigos)
        if self.npc:
            self.npc.draw(self.tela, self.camera_offset)
        
        # 3. Desenha inimigos
        for inimigo in [i for i in self.sala.inimigos if not i.dead or not i.animation_complete]:
            inimigo.draw(self.tela, self.camera_offset)

            # Desenha barra de vida do Boss se estiver na sala do boss
        if self.current_map == "map7":
            for inimigo in self.sala.inimigos:
                if isinstance(inimigo, Boss):
                    self._draw_boss_health(inimigo)

        
        # 4. Desenha o player
        player_pos = (
            self.player.rect.x - self.camera_offset[0],
            self.player.rect.y - self.camera_offset[1]
        )
        self.tela.blit(self.player.image, player_pos)
        
        # 5. Desenha a espada (na mesma camada que o player)
        self.sword.draw(self.tela)
        
        # 6. Desenha projéteis
        for inimigo in self.sala.inimigos:
            if hasattr(inimigo, 'desenhar_projeteis'):
                inimigo.desenhar_projeteis(self.tela, self.camera_offset)
        
        # 7. Desenha camadas superiores (que devem cobrir partes do cenário, mas não os personagens)
        self.map.draw_top_layers(self.tela, self.camera_offset)
        
        # 8. Desenha a barra de vida do player (UI, acima de tudo)
        self.player.draw(self.tela)
        # Desenha a caixa de diálogo do NPC (acima de tudo)

        if self.npc and self.npc.dialogo_ativo and self.npc.dialogo:
            self.npc.dialogo.draw(self.tela)


        
    def _draw_map(self):
        """Desenha o mapa atual com offset de câmera"""
        for layer in self.map.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.map.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        pos = (
                            x * self.map.tmx_data.tilewidth - self.camera_offset[0],
                            y * self.map.tmx_data.tileheight - self.camera_offset[1]
                        )
                        self.tela.blit(tile, pos)

    def _draw_entity(self, entity):
        """Versão simplificada do draw de entidades"""
        pos = (
            entity.rect.x - self.camera_offset[0],
            entity.rect.y - self.camera_offset[1]
        )
        self.tela.blit(entity.image, pos)

    def _draw_transition(self):
        transition = self.transition_data
        progress = transition['progress']
        
        # Fase de escurecer (0.0 a 0.5)
        if progress < 0.5:
            # Desenha tudo normalmente
            self._draw_game_elements()
            
            # Aplica fade progressivo
            alpha = int(255 * (progress * 2))  # 0 a 255
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, alpha))
            self.tela.blit(fade, (0, 0))
        
        # Ponto de transição (0.5) - momento mais escuro
        elif progress == 0.5:
            # Tela completamente preta
            self.tela.fill((0, 0, 0))
            
            # Aqui fazemos a troca real do mapa
            self.current_map = transition['new_map']
            self.map = self.maps[self.current_map]
            if 'target_pos' in transition:
                self.player.rect.topleft = transition['target_pos']
            self.calculate_camera_offset()
            
            # Gera novos inimigos
            self.sala.inimigos = []
            self.sala._definir_limites()
            self.sala.inimigos = self.sala.gerar_inimigos()
            self.sala.sala_limpa = False
            self._setup_npc()
        
        # Fase de clarear (0.5 a 1.0)
        else:
            # Desenha o novo estado
            self._draw_game_elements()
            
            # Aplica fade out progressivo
            alpha = int(255 * ((1.0 - progress) * 2))  # 255 a 0
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, alpha))
            self.tela.blit(fade, (0, 0))

    def update(self):   
        if self.game_over:
            # Para todas as músicas quando o jogador morre
            if self.faint_music_playing:
                pygame.mixer.music.stop()
                self.faint_music_playing = False
                
            # Verifica se morreu na sala do boss para triggerar a sequência
            if self.current_map == "map7" and not self.epic_sequence_active:
                self.trigger_epic_sequence()
                return
                
        # Mostra tela de restart apenas se não for no boss
            if self.current_map != "map7":
                self.show_game_over_screen()
            return
            
        if self.transition_cooldown > 0:
            self.transition_cooldown -= 1
        
        self.player.update()
        self.sword.update()
        self.sala.update()
        
        if self.player.is_dead:
            self.game_over = True
            # Para a música do boss se estiver tocando
            if self.boss_music_playing:
                pygame.mixer.music.stop()
                self.boss_music_playing = False
            return
            
        if self.npc:
            self.npc.update(self.dt)
            
            # Verifica interação
            keys = pygame.key.get_pressed()
            self.npc.check_interaction(keys)
        
        for inimigo in self.sala.inimigos:
            inimigo.update()
            # Atualiza projéteis se for um Atirador
            if hasattr(inimigo, 'update_projeteis'):
                inimigo.update_projeteis()

        for event in pygame.event.get():
            if event.type == pygame.USEREVENT + 1:
                if not self.faint_music_playing and self.epic_sequence_active:
                    self.play_faint_music()
            elif event.type == BOSS_MUSIC_EVENT:
                print("Tocando música do boss após 18s do vídeo.")
                self.play_music("boss_music")
                self.boss_music_playing = True
        
        self.calculate_camera_offset()
        
        if hasattr(self, 'transition_data') and self.transition_data is not None:
            self._update_transition()
        else:
            self._check_transitions()

            if self.player.is_dead:  # Agora verifica o atributo booleano diretamente
                self.game_over = True
                return
            # Para a música do boss se o jogador morrer
            if self.player.is_dead and self.boss_music_playing:
                pygame.mixer.music.stop()
                self.boss_music_playing = False

    def _update_transition(self):
        transition = self.transition_data
        transition['progress'] += 1 / (60 * transition['duration'])

        if transition['progress'] >= 0.5 and not transition.get('map_changed', False):
            self.current_map = transition['new_map']
            self.map = self.maps[self.current_map]
            if 'target_pos' in transition:
                self.player.rect.midbottom = transition['target_pos']
            
            # Configura o NPC para o novo mapa
            self._setup_npc()
            transition['map_changed'] = True

            # Se for o mapa do boss, dispara a intro
            if self.current_map == "map7" and not self.boss_intro_played:
                self.trigger_boss_intro()
        
        if transition['progress'] >= 1:
            self.transition_data = None
            self.transition_cooldown = 120
            
            # Gera inimigos APÓS a transição completar
            self.sala.inimigos = []
            self.sala._definir_limites()
            self.sala.inimigos = self.sala.gerar_inimigos()
            self.sala.sala_limpa = False

    def _check_transitions(self):
        if self.transition_cooldown > 0:
                return
        
        transition_layer = self.map.check_transition(self.player)
        if not transition_layer:
            return
        
        transition_rules = {

            #Mapa 1
            ("map1", "Transicao 1"): ("map2", (self.maps["map2"].width // 2, self.maps["map2"].height - 20)),

            #Mapa 2
            ("map2", "Transicao 1"): ("map3", (self.maps["map3"].width // 2, self.maps["map3"].height - 60)), # Transição para o mapa 3
            ("map2", "Transicao 2"): ("map1", (self.maps["map1"].width // 2, self.maps["map1"].height - 600)), # Transição para o mapa 1

            # Mapa 3
            ("map3", "Porta-Entrada"): ("map2", (self.maps["map2"].width // 2, self.maps["map2"].height - 230)), # Transição para o mapa 2
            ("map3", "Porta-salão"): ("map6", (self.maps["map6"].width // 2, self.maps["map6"].height - 230)), # Transição para o Salão Principal 
            ("map3", "Porta-dormitório"): ("map5", (self.maps["map5"].width - 500, self.maps["map5"].height //2 )), # Transição para o Dormitório
            ("map3", "Porta-cozinha"): ("map4", (self.maps["map4"].width - 120, self.maps["map4"].height // 2)),  # Transição para a Cozinha

            # Mapa 4(Cozinha)
            ("map4", "Entrada"): ("map3", (self.maps["map3"].width - 1300 , self.maps["map3"].height // 2)), # Transição para o mapa 3

            #Mapa 5(Dormitório)
            ("map5", "Entrada"): ("map3", (self.maps["map3"].width - 100, self.maps["map3"].height // 2)), # Transição para o mapa 3

            #Mapa 6(Mapa Boss)
            ("map6", "Porta-boss"): ("map7", (self.maps["map7"].width // 2, self.maps["map7"].height - 230)), # Transição para o mapa 7 (boss)
            ("map6", "Porta-Entrada"): ("map3", (self.maps["map3"].width // 2, self.maps["map3"].height - 100 )) # Transição para o mapa 3


            
        }

        if (self.current_map, transition_layer)in transition_rules:
            new_map, new_pos = transition_rules[(self.current_map, transition_layer)]
            self._start_transition(new_map, new_pos)
            
            # Aciona a intro do boss se for entrar no mapa 7
            if new_map == "map7":
                self.trigger_boss_intro()


    def _start_transition(self, new_map, target_pos):
        print(f"Iniciando transição para: {new_map}")  # Debug
        self.transition_data = {
            'active': True,
            'duration': 1.5,
            'progress': 0,
            'new_map': new_map,
            'target_pos': target_pos    
        }
        self.play_music(new_map)

    def set_volume(self, volume):
        """Define o volume da música (0.0 a 1.0)"""
        self.volume = max(0.0, min(1.0, volume))  # Garante que está entre 0 e 1
        if self.musica_atual:
            pygame.mixer.music.set_volume(self.volume)

    def play_music(self, map_name):
        """Toca a música correspondente ao mapa atual"""
        if map_name in self.musicas:
            # Se já está tocando a música correta, não faz nada
            if self.musica_atual == self.musicas[map_name] and not (map_name == "boss_music" and not self.boss_music_playing):
                return
                
            musica = self.musicas[map_name]
            try:
                # Configurações especiais para música de boss
                if map_name == "boss_music":
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
                    pygame.mixer.music.set_volume(min(1.0, self.volume * 1.5))
                    pygame.mixer.music.load(musica)
                    pygame.mixer.music.play(-1, fade_ms=2000)
                    self.boss_music_playing = True
                else:
                    pygame.mixer.music.load(musica)
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(self.volume)
                    self.boss_music_playing = False
                
                self.musica_atual = musica
                print(f"Tocando música: {musica}")
            except Exception as e:
                print(f"Erro ao reproduzir música {musica}: {e}")
                pygame.mixer.quit()
                pygame.mixer.init()
                try:
                    pygame.mixer.music.load(musica)
                    pygame.mixer.music.play(-1)
                    self.musica_atual = musica
                    if map_name == "boss_music":
                        self.boss_music_playing = True
                except Exception as e2:
                    print(f"Falha crítica ao reproduzir música: {e2}")
                    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and not self.tela_inicial_ativa:
                    self.sword.attack()

            if self.tela_inicial_ativa:
                self.show_initial_screens()
            elif not self.game_over:
                self.update()
                self.draw()
                self.dt = self.clock.tick(60) / 1000.0
            else:
                self.show_game_over_screen()

    def trigger_boss_intro(self):
        """Executa a sequência de introdução do boss"""
        if not self.boss_intro_played and self.current_map == "map7":
            try:
                print("Iniciando introdução do boss...")

                # 1. Para a música da dungeon imediatamente
                pygame.mixer.music.stop()
                self.musica_atual = None

                # 2. Inicia uma thread que espera 19s e toca a música
                import threading, time

                def delayed_music():
                    time.sleep(19)
                    print("Tocando música do boss após 19s da intro.")
                    self.play_music("boss_music")
                    self.boss_music_playing = True

                threading.Thread(target=delayed_music, daemon=True).start()

                # 3. Toca o vídeo da intro (bloqueante)
                self.play_video_with_audio_and_skip(self.boss_video_path, self.tela)

                # 4. Gera inimigos do boss se necessário
                if not any(isinstance(inimigo, Boss) for inimigo in self.sala.inimigos):
                    self.sala.inimigos = []
                    self.sala._definir_limites()
                    self.sala.inimigos = self.sala.gerar_inimigos()
                    self.sala.sala_limpa = False

                # 5. Troca sprite da espada
                base_dir = os.path.dirname(os.path.abspath(__file__))
                nova_espada_path = os.path.join(base_dir, "graphics", "nova_espada.png")
                self.sword.change_sprite(nova_espada_path)
                self.sword.damage *= 2

                self.boss_intro_played = True

            except Exception as e:
                print(f"ERRO na intro do boss: {e}")
                self.play_music("boss_music")
                self.boss_music_playing = True



    def _play_boss_intro_video(self):
        """Reproduz o vídeo da intro em um thread separado"""
        try:
            self.play_video_with_audio_and_skip(self.boss_video_path, self.tela)
        finally:
            self.boss_intro_video_done = True  

            


if __name__ == "__main__":
    jogo = Game()
    jogo.run()