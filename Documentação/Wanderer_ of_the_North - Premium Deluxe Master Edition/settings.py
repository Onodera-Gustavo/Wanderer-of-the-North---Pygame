import pygame as pg
import os

DEBUG_MODE = True
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH, HEIGHT = 1280, 735

pg.display.set_caption("Wanderer of the North")
clock = pg.time.Clock()


basic_entity_size = (60, 60)

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

def get_mask_rect(surf, top=0, left=0):
    """Returns minimal bounding rectangle of an image"""
    surf_mask = pg.mask.from_surface(surf)
    rect_list = surf_mask.get_bounding_rects()
    if rect_list:
        surf_mask_rect = rect_list[0].unionall(rect_list)
        surf_mask_rect.move_ip(top, left)
        return surf_mask_rect

def time_passed(start_time, duration):
    return pg.time.get_ticks() - start_time > duration
