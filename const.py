import pygame
import button
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Боже, царя храни!')

# устанвка ФПС

clock = pygame.time.Clock()
FPS = 60

# Переменные

GRAVITY = 0.7
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
# Действия
moving_left = False
moving_right = False
shoot = False
granata = False
granata_thrown = False

# Загрузка фоток и кнопок
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
vyhod_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
# Фон
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
# store tiles in a list
img_list = []
for t in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{t}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# Пуля
pulya_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# Граната
granata_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
# Бонусы
zdorovie_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
granata_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
predmet_boxes = {
    'Zdorovie': zdorovie_box_img,
    'Ammo': ammo_box_img,
    'Granata': granata_box_img
}

# Настройка цвета
BG = (144, 201, 120)


# Создаём кнопки
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
vyhod_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, vyhod_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

# Создаём группы объектов
enemy_group = pygame.sprite.Group()
pulya_group = pygame.sprite.Group()
granata_group = pygame.sprite.Group()
vzryv_group = pygame.sprite.Group()
predmet_box_group = pygame.sprite.Group()
ukrasheniya_group = pygame.sprite.Group()
voda_group = pygame.sprite.Group()
vyhod_group = pygame.sprite.Group()


# Создаём списокт айтлов
mir_data = [[-1] * COLS for _ in range(ROWS)]