import pygame as pg
import math

from settings import *

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
class Player:
    def __init__(self, x, y):
        self.image = pg.Surface((40, 40))
        self.image.fill(cores['vermelho'])
        self.rect = self.image.get_rect(center=(x, y))

        # Direção
        self.direction = pg.Vector2(1, 0)  # Direção inicial
        self.last_direction = pg.Vector2(1, 0)  # Última direção que o jogador andou

        # Dash
        self.dash_direction = pg.Vector2(0, 0)  # Nova variável para a direção do dash
        self.speed = 5
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

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Classe da Espada
class Sword:
    def __init__(self, player):
        self.radius = 50
        self.sword_angle = 0  # Variável para a direção da espada
        self.attack_rotation = 100  # Rotação inicial do ataque
        self.attack_direction = 1  # Direção do ataque (1 para direita, -1 para esquerda)
        self.attacking = False
        self.player = player
        self.hit_enemy = False  # Flag para impedir múltiplos hits no mesmo ataque

    def update(self):
        # Pega a posição do mouse
        mouse_x, mouse_y = pg.mouse.get_pos()

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
                self.attack_rotation = 100 * self.attack_direction  # Limita a rotação ao máximo de 160
                self.attacking = False  # Termina o ataque
                self.hit_enemy = False  # Reseta a flag de colisão para o próximo ataque

                # Inverte a direção do ataque para o próximo
                self.attack_direction *= -1

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.hit_enemy = False  # Permite que o próximo ataque cause dano

    def get_positions(self):
        """ Retorna as coordenadas do cabo e da ponta da espada """
        angle_rad = math.radians(self.sword_angle + self.attack_rotation)  # Converte o ângulo para radianos
        sword_tip_x = self.player.rect.centerx + self.radius * math.cos(angle_rad)  # Calcula a posição da ponta da espada
        sword_tip_y = self.player.rect.centery + self.radius * math.sin(angle_rad)  # Calcula a posição da ponta da espada
        return (self.player.rect.centerx, self.player.rect.centery), (sword_tip_x, sword_tip_y)  # Retorna as posições

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

# Classe do Inimigo
class Enemy:
    def __init__(self, x, y, health):
        self.image = pg.Surface((40, 40))
        self.image.fill(cores['verde'])
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health
        self.max_health = health
        self.health_bar = HealthBar(self.rect.centerx - 25, self.rect.top - 10, 50, 5, health)  
    
    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        self.health_bar.update(self.health)
        print(f"Inimigo recebeu {damage} de dano! Vida restante: {self.health}")

    def is_dead(self):
        return self.health <= 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.health_bar.x = self.rect.centerx - 25
        self.health_bar.y = self.rect.top - 10
        self.health_bar.draw(surface)

# Inicialização
player = Player(WIDTH // 2, HEIGHT // 2)
sword = Sword(player)
enemy = Enemy(WIDTH // 3, HEIGHT // 2, 100)

running = True
while running:
    screen.fill((0, 0, 0))
    keys = pg.key.get_pressed()
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            sword.attack()
    
    player.move(keys)
    sword.update()
    
    if enemy:
        if sword.attacking and sword.check_collision(enemy):  # Só dá dano uma vez por ataque
            enemy.take_damage(20)
            if enemy.is_dead():
                enemy = None  # Remove o inimigo se ele morrer

    # Desenha os elementos
    player.draw(screen)
    sword.draw(screen)
    
    if enemy:
        enemy.draw(screen)
    
    pg.display.flip()
    clock.tick(60)

pg.quit()

