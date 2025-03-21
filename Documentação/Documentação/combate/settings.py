
WIDTH, HEIGHT = 800, 600

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

# inimigos : vida, defesa, ataque, velocidade 
inimigos = {
    'Esqueleto Soldado': {
        'ataques': 10,
        'velocidade': 0.6,
        'vida': 120,
        'defesa': 3,
    },
    'Esqueleto Arqueiro': {
        'ataques': 7,
        'velocidade': 0.7,
        'vida': 80,
        'defesa': 1,
    },
    'Cultista Iniciado': {
        'ataques': 15,
        'velocidade': 0.7,
        'vida': 120,
        'defesa': 2,
    },
    'Cultista Sacerdote': {
        'ataques': 20,
        'velocidade': 0.5,
        'vida': 80,
        'defesa': 4,
    },
    'Cultista Diácono': {
        'ataques': 40,
        'velocidade': 0.3,
        'vida': 30,
        'defesa': 5,
    },
    'Demônio': {
        'ataques': 15,
        'velocidade': 0.5,
        'vida': 100,
        'defesa': 5,
    },
    'Aberração': {
        'ataques': 50,
        'velocidade': 0.2,
        'vida': 170,
        'defesa': 8,
    },
}