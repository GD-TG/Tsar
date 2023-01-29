import pygame
import os
import random
import csv
import button
import time
from const import *
pygame.init()

# Настройка шрифта
font = pygame.font.SysFont('Futura', 30)


# Сброс уровня
def reset_level():
    enemy_group.empty()
    pulya_group.empty()
    granata_group.empty()
    vzryv_group.empty()
    predmet_box_group.empty()
    ukrasheniya_group.empty()
    voda_group.empty()
    vyhod_group.empty()

    # create empty tile list
    data = [[-1] * COLS for _ in range(ROWS)]
    return data


# Обновление
def all_update():
    pulya_group.update()
    granata_group.update()
    vzryv_group.update()
    predmet_box_group.update()
    ukrasheniya_group.update()
    voda_group.update()
    vyhod_group.update()
    pulya_group.draw(screen)
    granata_group.draw(screen)
    vzryv_group.draw(screen)
    predmet_box_group.draw(screen)
    ukrasheniya_group.draw(screen)
    voda_group.draw(screen)
    vyhod_group.draw(screen)


# Вывод текста
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


class Czar(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, granaty):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.granaty = granaty
        self.zdorovie = 100
        self.max_zdorovie = self.zdorovie
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # Загрузка спратов
        animation = ['Idle', 'Run', 'Jump', 'Death']
        for a in animation:

            temp_list = []
            # Подсчёт спратов
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{a}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{a}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # Обновление выстрела
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # Сброс движения
        screen_scroll = 0
        dx = 0
        dy = 0

        # Движение
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Прыжок
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump, self.in_air = False, True

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Проверка столкновений
        for t in mir.obstacle_list:
            # По Х
            if t[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # Поворот врага
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # По У
            if t[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Проверка прыжка
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = t[1].bottom - self.rect.top
                # Проверка падения
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = t[1].top - self.rect.bottom

        # Проверка на попадание в воду
        if pygame.sprite.spritecollide(self, voda_group, False):
            self.zdorovie = 0

        # Вылет
        level_complete = False
        if pygame.sprite.spritecollide(self, vyhod_group, False):
            level_complete = True

        # Вылет с карты
        if self.rect.bottom > SCREEN_HEIGHT:
            self.zdorovie = 0

        # Вылет с карты
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # Перемещение
        self.rect.x += dx
        self.rect.y += dy

        # Обновление прокрутки
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll <
                (mir.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        # Выстрел
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            pulya = Pulya(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                          self.direction)
            pulya_group.add(pulya)

            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            # Столкновение с врагом
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # Обновление вида у врага
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # Скроллинг
        self.rect.x += screen_scroll

    def update_animation(self):
        # Обновление анимации
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # Сбрс
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Уникальность действия
        if new_action != self.action:
            self.action = new_action
            # Анимация
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.zdorovie <= 0:
            self.zdorovie = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Mir():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # Перебор файлв в папке
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    # Собвственно, создаём объекты
                    if tile in range(0, 9):
                        self.obstacle_list.append(tile_data)
                    elif tile in range(9, 11):
                        voda = Voda(img, x * TILE_SIZE, y * TILE_SIZE)
                        voda_group.add(voda)
                    elif tile in range(11, 15):
                        ukrashenuya = Ukrasheniya(img, x * TILE_SIZE, y * TILE_SIZE)
                        ukrasheniya_group.add(ukrashenuya)
                    elif tile == 15:
                        player = Czar('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        zdorovie_bar = ZdorovieBar(10, 10, player.zdorovie, player.zdorovie)
                    elif tile == 16:
                        enemy = Czar('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        predmet_box = PredmetBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        predmet_box_group.add(predmet_box)
                    elif tile == 18:
                        predmet_box = PredmetBox('Granata', x * TILE_SIZE, y * TILE_SIZE)
                        predmet_box_group.add(predmet_box)
                    elif tile == 19:
                        predmet_box = PredmetBox('Zdorovie', x * TILE_SIZE, y * TILE_SIZE)
                        predmet_box_group.add(predmet_box)
                    elif tile == 20:
                        vyhod = Vyhod(img, x * TILE_SIZE, y * TILE_SIZE)
                        vyhod_group.add(vyhod)

        return player, zdorovie_bar

    def draw(self):
        for t in self.obstacle_list:
            t[1][0] += screen_scroll
            screen.blit(t[0], t[1])


class Default(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Ukrasheniya(Default):
    def __init__(self, img, x, y):
        super().__init__(img, x, y)


class Voda(Default):
    def __init__(self, img, x, y):
        super().__init__(img, x, y)


class Vyhod(Default):
    def __init__(self, img, x, y):
        super().__init__(img, x, y)


class PredmetBox(pygame.sprite.Sprite):
    def __init__(self, predmet_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.predmet_type = predmet_type
        self.image = predmet_boxes[self.predmet_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # Скроллинг
        self.rect.x += screen_scroll
        # Проверка на сбор бонуса
        if pygame.sprite.collide_rect(self, player):
            # Определяем, какой бонус
            if self.predmet_type == 'Zdorovie':
                player.zdorovie += 25
                if player.zdorovie > player.max_zdorovie:
                    player.zdorovie = player.max_zdorovie
            elif self.predmet_type == 'Ammo':
                player.ammo += 15
            elif self.predmet_type == 'Granata':
                player.granaty += 3
            # Удаляем
            self.kill()


class ZdorovieBar():
    def __init__(self, x, y, zdorovie, max_zdorovie):
        self.x = x
        self.y = y
        self.zdorovie = zdorovie
        self.max_zdorovie = max_zdorovie

    def draw(self, zdorovie):
        # Обновляем полосу здоровья
        self.zdorovie = zdorovie

        ratio = self.zdorovie / self.max_zdorovie
        pygame.draw.rect(screen, (0, 0, 0), (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 150 * ratio, 20))


class Pulya(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = pulya_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # Вылет пули
        self.rect.x += self.direction * self.speed + screen_scroll
        # Прверка на вылет  за пределы поле или попадание в клетку уровня
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        for t in mir.obstacle_list:
            if t[1].colliderect(self.rect):
                self.kill()

        # Проверка на попадание во врага
        if pygame.sprite.spritecollide(player, pulya_group, False):
            if player.alive:
                player.zdorovie -= 5
                self.kill()
        for e in enemy_group:
            if pygame.sprite.spritecollide(e, pulya_group, False):
                if e.alive:
                    e.zdorovie -= 25
                    self.kill()


class Granata(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = granata_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # Прверерка на попадание в клетку уровня
        for t in mir.obstacle_list:
            # Если попал в стену
            if t[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # Если попал в землю
            if t[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # Коснулся
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = t[1].bottom - self.rect.top
                # Не коснулся
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = t[1].top - self.rect.bottom

        # Обновляем координаты
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # Проверяем таймер
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            vzryv = Vzryv(self.rect.x, self.rect.y, 0.5)
            vzryv_group.add(vzryv)
            # Наносим урон
            if abs(self.rect.centerx - player.rect.centerx) / 2 < TILE_SIZE and \
                    abs(self.rect.centery - player.rect.centery) / 2 < TILE_SIZE:
                player.zdorovie -= 50
            for e in enemy_group:
                if abs(self.rect.centerx - e.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - e.rect.centery) < TILE_SIZE * 2:
                    e.zdorovie -= 50


class Vzryv(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for n in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{n}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # Переход
        self.rect.x += screen_scroll

        VZRYV_SPEED = 4
        # Обновляем анимацию
        self.counter += 1

        if self.counter >= VZRYV_SPEED:
            self.counter = 0
            self.frame_index += 1
            # Если анимация завершена
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


# Грузим уровень
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            mir_data[x][y] = int(tile)
mir = Mir()
player, zdorovie_bar = mir.process_data(mir_data)

if __name__ == '__main__':
    run = True
    while run:
        clock.tick(FPS)
        if not start_game:
            # Загружаем меню
            screen.fill(BG)
            
            if start_button.draw(screen):
                start_game = True
            if vyhod_button.draw(screen):
                run = False
        else:
            # Загружаем мир
            draw_bg()
            mir.draw()
            zdorovie_bar.draw(player.zdorovie)
            draw_text('Пуль: ', font, (255, 255, 255), 10, 35)
            for x in range(player.ammo):
                screen.blit(pulya_img, (90 + (x * 10), 40))
            draw_text('Гранат: ', font, (255, 255, 255), 10, 60)
            for x in range(player.granaty):
                screen.blit(granata_img, (135 + (x * 15), 60))
            player.update()
            player.draw()
            for e in enemy_group:
                e.ai()
                e.update()
                e.draw()

            # Обновляем и рисуем группы оюъектов
            all_update()

            # Движение персонажа
            if player.alive:
                # Выстрел
                if shoot:
                    player.shoot()
                # Бросок гранаты
                elif granata and granata_thrown == False and player.granaty > 0:
                    granata = Granata(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                                      player.rect.top, player.direction)
                    granata_group.add(granata)
                    player.granaty -= 1
                    granata_thrown = True
                if player.in_air:
                    player.update_action(2)  # Прыжок
                elif moving_left or moving_right:
                    player.update_action(1)  # Бег
                else:
                    player.update_action(0)  # Без изменений
                screen_scroll, level_complete = player.move(moving_left, moving_right)
                bg_scroll -= screen_scroll
                # Переход на новый уровень
                if level_complete:
                    level += 1
                    bg_scroll = 0
                    mir_data = reset_level()
                    if level <= MAX_LEVELS:
                        # Грузим уровень
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    mir_data[x][y] = int(tile)
                        mir = Mir()
                        player, zdorovie_bar = mir.process_data(mir_data)
            else:
                screen.fill(BG)
                draw_text(f"Ваш результат -  {level}-й уровень",font,(0,255,0),300,100)
                screen_scroll = 0
                if restart_button.draw(screen):
                    bg_scroll = 0
                    mir_data = reset_level()
                    # Грузим уровень
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                mir_data[x][y] = int(tile)
                    mir = Mir()
                    player, zdorovie_bar = mir.process_data(mir_data)

        for event in pygame.event.get():

            # Выход
            if event.type == pygame.QUIT:
                run = False

            # Нажата кнопка
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE:
                    shoot = True
                if event.key == pygame.K_q:
                    granata = True
                if event.key == pygame.K_w and player.alive:
                    player.jump = True
                if event.key == pygame.K_ESCAPE:
                    run = False

            # Отжата кнопка
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_SPACE:
                    shoot = False
                if event.key == pygame.K_q:
                    granata = False
                    granata_thrown = False
        pygame.display.update()
    pygame.quit()
