import pygame as pg
import math

from settings import *
from random import randint

pg.init()

# Configurações da tela
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

# Cores
# cores['branco'] = (255, 255, 255)
# cores['vermelho'] = (255, 0, 0)
# cores['verde'] = (0, 255, 0)
# cores['azul'] = (0, 0, 255)

# Classe do Jogador
class Player(pg.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pg.image.load('graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.direction = pg.Vector2(1, 0)  # Direção inicial
        self.last_direction = pg.Vector2(1, 0)  # Última direção que o jogador andou

        # Variáveis de Combate
        self.health = 100
        self.shield = 100
        self.speed = 5

        # Variáveis de Dash
        self.dash_direction = pg.Vector2(0, 0)  # Nova variável para a direção do dash
        self.dash_speed = 15
        self.dashing = False
        self.dash_timer = 0
        self.dash_duration = 10
        self.dash_cooldown = 30
        self.dash_cooldown_timer = 0
        self.dash_pressed = False

    def move(self, keys):
        direction = pg.Vector2(0, 0)

        if keys[pg.K_a]:
            direction.x -= 1
        if keys[pg.K_d]:
            direction.x += 1
        if keys[pg.K_w]:
            direction.y -= 1
        if keys[pg.K_s]:
            direction.y += 1

        # Normalizando a direção para permitir movimentos diagonais
        if direction.length() > 0:
            direction.normalize_ip()
            self.last_direction = direction  # Atualiza a última direção quando o jogador se move

        if self.dashing:
            self.rect.x += self.dash_direction.x * self.dash_speed
            self.rect.y += self.dash_direction.y * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
                self.dash_cooldown_timer = self.dash_cooldown
        else:
            self.rect.x += direction.x * self.speed
            self.rect.y += direction.y * self.speed

            # Ativar o dash
            if keys[pg.K_q] and not self.dashing and self.dash_cooldown_timer <= 0 and not self.dash_pressed:
                # Se o jogador não estiver se movendo, utiliza a última direção
                if direction.length() == 0:
                    direction = self.last_direction
                self.dash_direction = direction  # Atualiza a direção do dash
                self.dashing = True
                self.dash_timer = self.dash_duration
                self.dash_pressed = True

        if not keys[pg.K_q]:
            self.dash_pressed = False

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1
    
    def take_damage(self, damage):
        self.shield = max(0, self.shield - damage)

        if self.shield < 0:
            self.shield = 0
            self.health = max(0, self.health - damage)

        if self.health < 0:
            self.health = 0
    
    def draw_health_bar(self):
        pg.draw.rect(screen, cores['cinza'], (20, 20, 200, 20))  # Fundo
        pg.draw.rect(screen, cores['azul'], (20, 20, max(0, self.shield * 2), 20))  # Escudo

        pg.draw.rect(screen, cores['cinza'], (20, 50, 200, 20))  # Fundo
        pg.draw.rect(screen, cores['vermelho'], (20, 50, max(0, self.health * 2), 20))  # Vida

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class CameraGroup(pg.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pg.display.get_surface()
        
        # Camera movimentação
        self.offset = pg.math.Vector2()  # Controla a posição da câmera
        self.half_w = self.display_surface.get_size()[0] // 2  # Metade da largura da tela
        self.half_h = self.display_surface.get_size()[1] // 2  # Metade da altura da tela

        # Criação do chão
        self.ground_surf = pg.image.load('graphics/ground.png').convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(topleft=(0, 0))

    def center_target_camera(self, target):
        """ Mantém a câmera centralizada no jogador """
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player):
        """ Desenha os elementos com base na posição da câmera """
        self.center_target_camera(player)

        # Desenha o chão ajustando pelo offset da câmera
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surf, ground_offset)

        # Organiza os sprites por profundidade e desenha ajustando pelo offset
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)



# Classe da Espada
class Sword:
    def __init__(self, player, camera_group):
        self.radius = 50
        self.sword_angle = 0  # Variável para a direção da espada
        self.attack_rotation = 100  # Rotação inicial do ataque
        self.attack_direction = 1  # Direção do ataque (1 para direita, -1 para esquerda)
        self.attacking = False
        self.player = player
        self.hit_enemy = False  # Flag para impedir múltiplos hits no mesmo ataque
        self.camera_group = camera_group  # Referência ao grupo da câmera

    def update(self):
        # Pega a posição do mouse ajustada pela câmera
        mouse_x, mouse_y = pg.mouse.get_pos()
        mouse_x += self.camera_group.offset.x
        mouse_y += self.camera_group.offset.y

        # Calcula o vetor direção do jogador até o mouse
        mouse_vector = pg.Vector2(mouse_x - self.player.rect.centerx, self.player.rect.centery - mouse_y)

        # Calcula o ângulo para o mouse
        if mouse_vector.length() > 0:
            self.sword_angle = mouse_vector.angle_to(pg.Vector2(1, 0))  # Calcula o ângulo entre o vetor e o eixo X

        if self.attacking:
            # Se o ataque está em progresso, atualiza a rotação
            self.attack_rotation += 15 * self.attack_direction  # Aplica a rotação dependendo da direção

            # Condição de finalização do ataque (se a rotação atingir o limite)
            if abs(self.attack_rotation) >= 100:
                self.attack_rotation = 100 * self.attack_direction  # Limita a rotação ao máximo de 100
                self.attacking = False  # Termina o ataque
                self.hit_enemy = False  # Reseta a flag de colisão para o próximo ataque

                # Inverte a direção do ataque para o próximo
                self.attack_direction *= -1

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.hit_enemy = False  # Permite que o próximo ataque cause dano

    def get_positions(self):
        """ Retorna as coordenadas do cabo e da ponta da espada ajustadas pela câmera """
        angle_rad = math.radians(self.sword_angle + self.attack_rotation)  # Converte o ângulo para radianos
        
        # Vetor unitário para a direção da espada
        direction_vector = pg.Vector2(math.cos(angle_rad), math.sin(angle_rad))

        # Ajusta a posição inicial 15 pixels para baixo
        handle_x = self.player.rect.centerx
        handle_y = self.player.rect.centery + 15

        # Corrige a ponta da espada para manter o tamanho correto
        sword_tip_x = handle_x + direction_vector.x * self.radius
        sword_tip_y = handle_y + direction_vector.y * self.radius

        # Ajusta a posição pela câmera
        offset_x = self.camera_group.offset.x
        offset_y = self.camera_group.offset.y

        return (handle_x - offset_x, handle_y - offset_y), (sword_tip_x - offset_x, sword_tip_y - offset_y)




    def check_collision(self, enemy):
        """ Verifica se qualquer parte da espada atinge o inimigo """
        if self.hit_enemy:  # Se já acertou, não pode causar outro hit
            return False

        (x1, y1), (x2, y2) = self.get_positions()

        for i in range(0, 101):  # Divide a linha em 100 pontos
            px = x1 + (x2 - x1) * i / 100
            py = y1 + (y2 - y1) * i / 100
            if enemy.rect.collidepoint(px, py):  # Se acertar, marca que já houve hit
                self.hit_enemy = True
                return True
        return False

    def draw(self, surface):
        pg.draw.line(surface, cores['branco'], *self.get_positions(), 5)


# Classe da Barra de Vida
class HealthBar:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.max_hp = max_hp
        self.hp = max_hp
    
    def update(self, current_hp):
        self.hp = current_hp
    
    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pg.draw.rect(surface, cores['vermelho'], (self.x, self.y, self.w, self.h))
        pg.draw.rect(surface, cores['verde'], (self.x, self.y, self.w * ratio, self.h))

class Projectile:
    def __init__(self, x, y, direction, speed, owner):
        self.image = pg.Surface((10, 10))
        self.image.fill(cores['azul'])  # Cor do projétil
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        if self.direction.length() != 0:  # Garante que o vetor não seja zero
            self.direction = self.direction.normalize()
        self.speed = speed
        self.owner = owner
        self.reflected = False
    
    def move(self):
        """Move o projétil com base na direção e velocidade"""
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
    
    def reflect(self):
        """Reflete a direção do projétil"""
        self.direction = -self.direction
        self.reflected = True

    def is_on_screen(self, surface_width, surface_height):
        """Verifica se o projétil ainda está dentro da tela"""
        return self.rect.x > 0 and self.rect.x < surface_width and self.rect.y > 0 and self.rect.y < surface_height
    
    def draw(self, surface):
        """Desenha o projétil na tela"""
        surface.blit(self.image, self.rect)



# Classe do Inimigo Esqueleto 'Soldado'
class SkeletonSoldier:
    def __init__(self, x, y, health, speed):
        # Variáveis de Posição e Aparência
        self.image = pg.Surface((40, 40))
        self.image.fill((0, 255, 0))  # Verde
        self.rect = self.image.get_rect(center=(x, y))

        # Variáveis de Estado
        self.health = health
        self.max_health = health
        self.speed = speed
        self.dead = False

        # Barra de Vida
        self.health_bar = HealthBar(self.rect.centerx - 25, self.rect.top - 10, 50, 5, health)

        # Variáveis de Combate
        self.attacking = False
        self.attack_cooldown = 25  # Cooldown de ataque (frames)
        self.attack_timer = 0  # Contador para ataque

    def update(self, player):
        """ Atualiza o inimigo a cada frame """
        if self.health <= 0:
            self.dead = True

        if not self.dead:
            self.move()

            # Verifica colisão com o jogador e gerencia ataque
            if self.rect.colliderect(player.rect):
                self.attack(player)

        # Atualiza barra de vida
        self.health_bar.update(self.health)

    def move(self):
        """ Movimenta o inimigo """
        if not self.attacking and self.health > 0:
            # Movimentação simples (substituir por IA melhor)
            self.rect.x -= self.speed  # Exemplo: Move para a esquerda

    def attack(self, player):
        """ Ataca o jogador caso esteja em contato """
        if self.attack_timer <= 0:
            self.attacking = True
            player.take_damage(5)
            self.attack_timer = self.attack_cooldown  # Reseta cooldown
        else:
            self.attack_timer -= 1  # Reduz cooldown a cada frame

    def take_damage(self, damage):
        """ Reduz a vida do inimigo e atualiza a barra de vida """
        self.health = max(0, self.health - damage)
        self.health_bar.update(self.health)
    
    def is_dead(self):
        return self.health <= 0

    def draw(self, surface):
        """ Desenha o inimigo e sua barra de vida na tela """
        surface.blit(self.image, self.rect)
        self.health_bar.x = self.rect.centerx - 25
        self.health_bar.y = self.rect.top - 10
        self.health_bar.draw(surface)


# Classe do Inimigo Esqueleto 'Atirador'
class SkeletonArcher:
    def __init__(self, x, y, health, speed):
        # Variáveis de Posição e Aparência
        self.image = pg.Surface((40, 40))
        self.image.fill(cores['verde'])  
        self.rect = self.image.get_rect(center=(x, y))

        # Variáveis de Movimento
        self.speed = speed
        self.moving = False

        # Variáveis de Combate
        self.health = health
        self.max_health = health
        self.health_bar = HealthBar(self.rect.centerx - 25, self.rect.top - 10, 50, 5, health)

        # Variáveis de Ataque
        self.projectiles = []
        self.shoot_timer = 30  # Tempo entre tiros (30 frames = 0.5 segundos)
        self.attacking = False

    def take_damage(self, damage):
        """Reduz a vida do inimigo e atualiza a barra de vida"""
        self.health = max(0, self.health - damage)
        self.health_bar.update(self.health)
        print(f"Inimigo recebeu {damage} de dano! Vida restante: {self.health}")

    def is_dead(self):
        """Verifica se o inimigo morreu"""
        return self.health <= 0

    def shoot(self, player):
        """Faz o arqueiro atirar um projétil no jogador"""
        if self.shoot_timer <= 0:
            direction = pg.Vector2(player.rect.center) - pg.Vector2(self.rect.center)
            direction = direction.normalize()  # Normaliza o vetor para manter velocidade constante
            self.projectiles.append(Projectile(self.rect.centerx, self.rect.centery, direction, 5, self))
            self.shoot_timer = 30  # Reinicia o timer de tiro

    def update(self, player):
        """Atualiza o arqueiro (movimento, ataque e projéteis)"""
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        if not self.is_dead():
            self.shoot(player)

        # Atualiza projéteis e remove os que saíram da tela
        self.projectiles = [proj for proj in self.projectiles if proj.is_on_screen(800, 600)]  # Substitua as dimensões da tela
        for projectile in self.projectiles:
            projectile.move()

    def draw(self, surface):
        """Desenha o arqueiro e seus projéteis na tela"""
        surface.blit(self.image, self.rect)
        self.health_bar.x = self.rect.centerx - 25
        self.health_bar.y = self.rect.top - 10
        self.health_bar.draw(surface)

        for projectile in self.projectiles:
            projectile.draw(surface)

# Inicialização
camera_group = CameraGroup()
player = Player((200,500), camera_group)
sword = Sword(player, camera_group)
shooter_enemy = SkeletonArcher(WIDTH // 3, HEIGHT // 2, 100, 5)
soldier_enemy = SkeletonSoldier(WIDTH // 3 * 2, HEIGHT // 2, 100, 5)

running = True
while running:
    screen.fill((0, 0, 0))
    keys = pg.key.get_pressed()
    
    camera_group.update()
    camera_group.custom_draw(player)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            sword.attack()
    
    player.move(keys)
    sword.update()
    
    if soldier_enemy is not None:
        soldier_enemy.update(player)
        soldier_enemy.draw(screen)
            
        if sword.attacking and sword.check_collision(soldier_enemy):  # Só dá dano uma vez por ataque
            soldier_enemy.take_damage(20)
            
        if soldier_enemy.is_dead():
            soldier_enemy = None  # Remove o inimigo se ele morrer

    if shooter_enemy is not None:
        shooter_enemy.update(player)
        shooter_enemy.draw(screen)
        for projectile in shooter_enemy.projectiles[:]:
            if shooter_enemy.is_dead():
                shooter_enemy = None
            
            if shooter_enemy is projectile.owner and player.rect.colliderect(projectile.rect):
                player.take_damage(5)
                shooter_enemy.projectiles.remove(projectile)
                
            if sword.attacking and not projectile.reflected and sword.check_collision(projectile):
                projectile.reflect()
            
            if projectile.reflected and shooter_enemy.rect.colliderect(projectile.rect):
                shooter_enemy.take_damage(randint(50, 200))
                shooter_enemy.projectiles.remove(projectile)
                
            if sword.attacking and sword.check_collision(shooter_enemy):  # Só dá dano uma vez por ataque
                shooter_enemy.take_damage(20)
                
              # Remove o inimigo se ele morrer

    # Desenha os elementos
    player.draw_health_bar()
    sword.draw(screen)
    player.draw(screen) 



    pg.display.flip()
    clock.tick(60)

pg.quit()