import pygame
from pytmx import load_pygame, TiledTileLayer

class Map:
    def __init__(self, tmx_file):
        self.tmx_data = load_pygame(tmx_file, load_all_tilesets=True)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

        # Debug: Verificar tamanho do mapa
        print(f"Mapa carregado: {tmx_file}")
        print(f"Largura: {self.width}, Altura: {self.height}")
        
        self.collision_layers = ["Colisao", "Paredes", "Objetos", "Paredes", "Cristal1", "Cristal2", "Pilar", "Trono", "Estátua"]
        self.transition_layers = ["Transicao 1", "Transicao 2", "Porta-cozinha","Porta-Entrada" ,"Porta-salão", "Porta-dormitório", "Porta-boss", "Entrada"]
        self.ysort_layers = ["YSort"]
        self.top_layers = ["Extras", "Bush", "Bush2", "Bush3", "Bush4", "Mountaincave", "Fields3", 
                           "Entrada","Adorno","Iluminação","Ornamentos","Estátua", "Objetos","Luminária","Porta-Entrada",
                           "Porta-boss","Porta", "Porta-salão", "Porta-dormitório", "Porta-cozinha",
                           "Paredes","Cristal1", "Cristal2", "Pilar",
                           "Trono"]
        
        self._prepare_masks()

    def _prepare_masks(self):
        self.collision_masks = {}
        self.transition_masks = {}
        
        # Cria uma superfície combinada para todas as camadas de colisão
        collision_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        has_collision = False
        
        for layer_name in self.collision_layers:
            try:
                layer = self.tmx_data.get_layer_by_name(layer_name)
                if layer and isinstance(layer, TiledTileLayer):
                    # Desenha os tiles na superfície de colisão combinada
                    for x, y, gid in layer:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            pos = (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                            collision_surface.blit(tile, pos)
                            has_collision = True
                            
            except ValueError:
                print(f"Camada {layer_name} não encontrada")
        
        # Cria uma única máscara para todas as colisões
        if has_collision:
            self.collision_mask = {
                'mask': pygame.mask.from_surface(collision_surface),
                'rect': pygame.Rect(0, 0, self.width, self.height)
            }
        else:
            self.collision_mask = None

        # Prepara máscaras de transição
        for layer_name in self.transition_layers:
            try:
                layer = self.tmx_data.get_layer_by_name(layer_name)
                if layer and isinstance(layer, TiledTileLayer):
                    mask_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    
                    for x, y, gid in layer:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            pos = (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                            mask_surface.blit(tile, pos)
                    
                    self.transition_masks[layer_name] = {
                        'mask': pygame.mask.from_surface(mask_surface),
                        'rect': pygame.Rect(0, 0, self.width, self.height)
                    }
            except ValueError:
                print(f"Camada {layer_name} não encontrada")

    def check_collision(self, entity):
        """Verifica colisão para qualquer entidade com rect"""
        # Verifica primeiro se a entidade está fora dos limites do mapa
        if not (0 <= entity.rect.left <= self.width and 0 <= entity.rect.top <= self.height):
            return True
        
        # Verifica se há máscara de colisão
        if not self.collision_mask:
            return False
            
        entity_mask = entity.mask if hasattr(entity, 'mask') else None
        
        # Se não tiver máscara, usa o retângulo de colisão
        if entity_mask is None:
            for layer in self.collision_layers:
                try:
                    collision_layer = self.tmx_data.get_layer_by_name(layer)
                    if collision_layer:
                        for x, y, gid in collision_layer:
                            tile = self.tmx_data.get_tile_image_by_gid(gid)
                            if tile:
                                tile_rect = pygame.Rect(
                                    x * self.tmx_data.tilewidth,
                                    y * self.tmx_data.tileheight,
                                    self.tmx_data.tilewidth,
                                    self.tmx_data.tileheight
                                )
                                if entity.rect.colliderect(tile_rect):
                                    return True
                except ValueError:
                    continue
            return False
        else:
            # Usa máscara de colisão se disponível
            offset = (
                self.collision_mask['rect'].x - entity.rect.x, 
                self.collision_mask['rect'].y - entity.rect.y
            )
            return bool(entity_mask.overlap(self.collision_mask['mask'], offset))

    def check_transition(self, player):
        # Verifica se há inimigos vivos na sala
        if hasattr(player, 'game') and hasattr(player.game, 'sala'):
            if not player.game.sala.sala_limpa:
                return None
        
        player_mask = player.mask
        player_rect = player.rect
        
        for layer_name, layer_data in self.transition_masks.items():
            offset = (layer_data['rect'].x - player_rect.x, 
                    layer_data['rect'].y - player_rect.y)
            
            if player_mask.overlap(layer_data['mask'], offset):
                return layer_name
        return None

    def resolve_collision(self, player):
        if self.check_collision(player):
            player.rect = player.old_rect.copy()
            return True
        return False

    def draw(self, surface, camera_offset=None):
        """Método principal de desenho do mapa (mantido para compatibilidade)"""
        if camera_offset is None:
            camera_offset = [0, 0]
        
        # Desenha apenas as camadas de fundo
        self.draw_background(surface, camera_offset)
        
        # Desenha camadas superiores
        self.draw_top_layers(surface, camera_offset)
            
        # 3. Camadas superiores
        for layer in self.tmx_data.visible_layers:
             if isinstance(layer, TiledTileLayer) and layer.name in self.top_layers:
                 self._draw_layer(surface, layer, camera_offset)
    
    def _draw_layer(self, surface, layer, camera_offset):
        for x, y, gid in layer:
            tile = self.tmx_data.get_tile_image_by_gid(gid)
            if tile:
                pos = (x * self.tmx_data.tilewidth - camera_offset[0], 
                       y * self.tmx_data.tileheight - camera_offset[1])
                surface.blit(tile, pos)
    
    def draw_background(self, surface, camera_offset=None):
        """Desenha apenas as camadas de fundo"""
        if camera_offset is None:
            camera_offset = [0, 0]
        
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer) and layer.name not in self.ysort_layers + self.top_layers + self.collision_layers + self.transition_layers:
                self._draw_layer(surface, layer, camera_offset)
    
    def draw_top_layers(self, surface, camera_offset=None):
        """Desenha apenas as camadas superiores (que devem cobrir o player)"""
        if camera_offset is None:
            camera_offset = [0, 0]
        
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer) and layer.name in self.top_layers:
                self._draw_layer(surface, layer, camera_offset)