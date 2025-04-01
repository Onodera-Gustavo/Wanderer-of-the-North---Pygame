import pygame as pg


WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Wanderer of the North")
clock = pg.time.Clock()

#Cores 
cores = {
    "branco": (255, 255, 255),
    "preto": (0, 0, 0),
    "vermelho": (255, 0, 0),
    "verde": (0, 255, 0),
    "azul": (0, 0, 255),
    "amarelo": (255, 255, 0),
    "ciano": (0, 255, 255),
    "magenta": (255, 0, 255),
    "cinza": (128, 128, 128),
    "cinza_claro": (192, 192, 192),
}


def time_passed(time, amount):
    if pg.time.get_ticks() - time > amount:
        time = pg.time.get_ticks()
        return True