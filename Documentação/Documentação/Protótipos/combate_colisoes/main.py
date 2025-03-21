import pygame
import math

pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Classe do Jogador
class Player:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = 1  # 1 = Direita, -1 = Esquerda
        
    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
            self.direction = -1  # Se move para a esquerda
            
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
            self.direction = 1  # Se move para a direita
    
        if keys[pygame.K_UP]:
            self.rect.y -= 5
        if keys[pygame.K_DOWN]:
            self.rect.y += 5
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Classe da Espada
class Sword:
    def __init__(self, player):
        self.radius = 50
        self.angle = 0  # Ângulo inicial em graus
        self.orbit_speed = 10  # Velocidade de órbita
        self.attack_rotation = 0  # Para controlar o giro no ataque
        self.attacking = False
        self.player = player
        
    def update(self):
        if self.attacking:
            self.attack_rotation += 20 * self.player.direction
            if abs(self.attack_rotation) >= 180:
                self.attack_rotation = 0
                self.attacking = False
        else:
            # Mantém a espada do lado correto do jogador
            if self.player.direction == 1:
                self.angle = -60  # Espada à direita
            else:
                self.angle = -120  # Espada à esquerda
        
        self.angle %= 360  # Mantém o ângulo dentro de 0-360 graus
    
    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.attack_rotation = 0
    
    def draw(self, surface):
        # Calcula a posição com base no ângulo e na direção do jogador
        angle_rad = math.radians(self.angle + self.attack_rotation)
        sword_x = self.player.rect.centerx + self.radius * math.cos(angle_rad)
        sword_y = self.player.rect.centery + self.radius * math.sin(angle_rad)
        
        pygame.draw.line(surface, WHITE, self.player.rect.center, (sword_x, sword_y), 5)

# Inicialização
player = Player(WIDTH // 2, HEIGHT // 2)
sword = Sword(player)

running = True
while running:
    screen.fill((0, 0, 0))
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            sword.attack()
    
    player.move(keys)
    sword.update()
    
    player.draw(screen)
    sword.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
