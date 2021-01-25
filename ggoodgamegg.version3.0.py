import pygame
import sys
import os
from math import ceil

WIDTH = 1000
HEIGHT = 800

FPS = 60


def load_image(name, colorkey=None):
    # загружаем изображения
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    # загружаем уровень
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    for i in range(len(level_map)):
        level_map[i] = list(level_map[i].ljust(max_width, '.'))
    return level_map


def generate_level(level):
    # генерируем уровень, расставляем платформы, монетки, врагов
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            if level[y][x] == '/':
                Tile('surface', x, y)
            if level[y][x] == '#':
                Tile('beautiful_surface', x, y)
            if level[y][x] == '1':
                Enemy(x, y)
            if level[y][x] == '?':
                Tile('enemy', x, y)
            if level[y][x] == ',':
                Tile('coin', x, y)
            if level[y][x] == "!":
                Tile("table", x, y)
            if level[y][x] == '@':
                new_player = Player(x, y)
    return new_player


def draw_hearts(lives):
    global hearts_group
    hearts_group = pygame.sprite.Group()
    for i in range(lives):
        heart = pygame.sprite.Sprite()
        heart.image = heart_image
        heart.rect = heart.image.get_rect()
        heart.rect.top = 10
        heart.rect.left = i * 50 + 50
        heart.add(hearts_group)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["THE",
                  "SUITEHEARTS",
                  "press any button to start"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    coun = 0
    text_coord = 150
    for line in intro_text:
        if coun == 0:
            font = pygame.font.Font("data/pixel3.ttf", 180)
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 350
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        elif coun == 1:
            font = pygame.font.Font("data/pixel3.ttf", 80)
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 250
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        else:
            font = pygame.font.Font("data/pixel3.ttf", 20)
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 350
            intro_rect.top = text_coord
            intro_rect.x = 350
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        coun += 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def end_screen():
    screen.fill((0, 0, 0))
    pixel_font = pygame.font.Font('data/pixel3.ttf', 108)
    pixel_font2 = pygame.font.Font('data/pixel3.ttf', 40)
    title = pixel_font.render('you lose!', 1, (255, 255, 255))
    title_rect = title.get_rect(left=220, top=150)
    screen.blit(title, title_rect)

    image = pygame.transform.scale(load_image("finalri.png"), (200, 200))
    screen.blit(image, (400, 400))

    motivation = pixel_font2.render('But determination is still burning', 1, (255, 255, 255))
    motivation_rect = motivation.get_rect(left=120, top=290)
    motivation2 = pixel_font2.render('in the depth of your heart. Lets try again!', 1, (255, 255, 255))
    motivation_rect2 = motivation.get_rect(left=100, top=320)
    screen.blit(motivation, motivation_rect)
    screen.blit(motivation2, motivation_rect2)

    button_group = pygame.sprite.Group()
    restart_btn = Button('restart', 200, 700, button_group)
    quit_btn = Button('quit', 600, 700, button_group)
    pygame.time.set_timer(pygame.USEREVENT, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    restart()
                    return
                if quit_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    terminate()
            if event.type == pygame.USEREVENT:
                for btn in button_group:
                    if btn.rect.collidepoint(pygame.mouse.get_pos()):
                        btn.timer += 1
                        btn.timer2 = 0
                    else:
                        btn.timer = 0
                        btn.timer2 += 1
                        btn.highlight()
        for btn in button_group:
            if btn.rect.collidepoint(pygame.mouse.get_pos()):
                btn.highlight()
        button_group.update()
        pygame.display.flip()
        clock.tick(FPS)


def restart():
    global player, camera
    for sprite in all_sprites:
        all_sprites.remove(sprite)
    for sprite in enemy_group:
        enemy_group.remove(sprite)
    for sprite in player_group:
        player_group.remove(sprite)
    for sprite in surface_group:
        surface_group.remove(sprite)
    for sprite in coin_group:
        coin_group.remove(sprite)
    camera = Camera()
    camera.update(player)
    player = generate_level(level_map)
    draw_hearts(player.lives)


class Button(pygame.sprite.Sprite):
    def __init__(self, text, pos_x, pos_y, group):
        super().__init__(group)
        self.font = pygame.font.Font('data/pixel3.ttf', 64)
        self.text = self.font.render(text, 1, (255, 255, 255))
        self.rect = self.text.get_rect(top=pos_y, left=pos_x)
        self.timer = 0
        self.timer2 = 0
        screen.blit(self.text, self.rect)

    def highlight(self):
        for i in range(self.rect.width // 10):
            if i < self.timer:
                pygame.draw.rect(screen, (255, 255, 255),
                                 (int(self.rect.left + i * 10), int(self.rect.bottom + 5), 9, 9))
        if self.timer == 0:
            for i in range(self.rect.width // 10 + 1):
                if i <= self.timer2:
                    pygame.draw.rect(screen, (0, 0, 0),
                                     (int(self.rect.right - (i + 1) * 10), int(self.rect.bottom + 5), 10, 9))


class Tile(pygame.sprite.Sprite):
    # отрисовываем объекты
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        if tile_type == 'surface' or tile_type == 'beautiful_surface':
            self.add(surface_group)
        elif tile_type == 'coin':
            self.add(coin_group)
        elif tile_type == 'enemy':
            self.add(enemy_group)
        self.pos_x = pos_x
        self.image = pygame.transform.scale(tile_images[tile_type], (tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        # изменяем положение обьектов, в соотвествии с камерой
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = 0
        self.dy = 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = tile_images['enemy_1']
        self.image = pygame.transform.scale(self.image, (90, 110))
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]
        self.speedx = - 80
        self.step = 0
        self.left = False

        self.frames = []
        self.cut_sheet(self.image, 3, 1)
        self.cur_frame = 1
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (97, 130))
        self.enemy_image = self.image
        self.rect = self.image.get_rect()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.step += 1
        self.change_frame()
        if self.step >= 100:
            self.step = 0
            self.speedx = - self.speedx
            self.left = not self.left
        self.abs_pos[0] += self.speedx * FPS / 1000

    def change_frame(self):
        self.cur_frame = self.cur_frame + 0.1
        self.enemy_image = self.frames[round(self.cur_frame) % len(self.frames)]
        self.enemy_image = pygame.transform.scale(self.enemy_image, (97, 130))
        self.image = pygame.transform.flip(self.enemy_image, self.left, False)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.speedx = 0
        self.speedy = 0

        self.coins = 0
        self.lives = 3
        self.timer = 0

        self.damage = False
        self.left = False
        self.bad_moment = False
        self.jump = False
        self.start_camera_dy = 0

        self.frames = []
        self.cut_sheet(load_image('hero1.png'), 3, 1)
        self.cur_frame = 1
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (97, 130))
        self.player_image = self.image  # копия картинки персонажа, нужна для того чтобы по ней переворачивать картинку персонажа при ходьбе
        self.rect = pygame.Rect(0, 0, self.image.get_width() - 20, self.image.get_height())

        self.rect.left = pos_x * tile_width
        self.rect.centery = pos_y * tile_height

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def get_keys(self):
        # проверяем какие клавиши нажаты, задаем скорость ходьбы
        keystate = pygame.key.get_pressed()
        self.speedx = 0
        if keystate[pygame.K_LEFT]:
            self.left = True
            if not self.collision_at_the_left():
                self.speedx = - 5
        if keystate[pygame.K_RIGHT]:
            self.left = False
            if not self.collision_at_the_right():
                self.speedx = 5
        if keystate[pygame.K_UP] and self.on_the_ground() and not self.collision_at_the_top():
            self.speedy = - 8
            if not self.bad_moment:
                # сохраняем начальное положение камеры перед прыжком, чтобы проверять не сместилась ли камера
                self.start_camera_dy = camera.dy
            self.rect.y -= 0.4  # чтобы 3не было пересечений с полом
            self.jump = True
            camera.dy += 0.4
        # анимация ходьбы, если ни одна клавиша не нажата, то оставляем 1 frame
        if any(keystate):
            self.change_frame()
        else:
            self.cur_frame = 1
            self.change_frame()

    def update(self):
        self.get_coins()
        # проверяем падает ли наш персонаж
        if not self.on_the_ground() and not self.collision_at_the_top():
            self.speedy += 0.4
            self.cur_frame = 0
            self.change_frame()
        else:
            self.speedy = 0

        # проверяем, что наш игрок не ушел за границы карты
        if self.rect.left < 300 and camera.dx != 0:
            self.rect.left = 300
        if self.rect.right > WIDTH - 300 and camera.dx != -len(level_map[0]) * tile_width + WIDTH:
            self.rect.right = WIDTH - 300

        # перемещаем игрока с проверкой, не уходит ли он за границы карты
        if self.rect.right + self.speedx <= WIDTH and self.rect.left + self.speedx >= 0:
            self.rect.x += self.speedx
        self.rect.y += self.speedy
        # без этого будет казаться, что где-то он ходит быстрее, а где-то медленнее
        if self.rect.right > WIDTH - 300 or self.rect.left < 300:
            self.speedx *= 1.5
        # перемещаем камеру, если мы не достигли конца/начала карты
        if not (self.rect.right >= WIDTH - 300 and camera.dx == -len(level_map[0]) * tile_width + WIDTH) and not \
                (self.rect.left < 300 and camera.dx == 0):
            camera.dx -= self.speedx
        camera.dy -= self.speedy
        # self.bad_moment - отвечает за смещение камеры, когда наш персонаж стукается о платформу сверху,
        # чтобы камера возвращалась в положение до прыжка
        if self.bad_moment and self.on_the_ground():
            camera.dy = self.start_camera_dy
            self.bad_moment = False
        # проверяем, чтобы наша камера не уходила за границы уровня
        if camera.dx > 0:
            camera.dx = 0
        if camera.dx < -len(level_map[0]) * tile_width + WIDTH:
            camera.dx = -len(level_map[0]) * tile_width + WIDTH
        if camera.dy < tile_height * 3:
            camera.dy = tile_height * 3
        # изменяем положение объектов относительно камеры
        for sprite in all_sprites:
            if sprite != self and sprite not in player_group:
                camera.apply(sprite)
        # проверяем столкновение с врагом
        if self.timer == 1:
            self.damage = False
        for _ in pygame.sprite.spritecollide(self, enemy_group, False):
            if not self.damage:
                self.lives -= 1
                self.damage = True
                self.timer = 0
                pygame.time.set_timer(pygame.USEREVENT, 1500)
                draw_hearts(self.lives)
        if self.lives == 0:
            self.death()

    def drop(self):
        for x in range(self.image.get_width()):
            for y in range(self.image.get_height()):
                r = self.image.get_at((x, y))[0]
                r = r + 50 if r < 205 else 255
                g = self.image.get_at((x, y))[1]
                g -= 50 if g > 50 else 0
                b = self.image.get_at((x, y))[2]
                b -= 50 if b > 50 else 0
                a = self.image.get_at((x, y))[3]
                self.image.set_at((x, y), pygame.Color(r, g, b, a))
                self.player_image = self.image

    def change_frame(self):
        # анимация ходьбы
        self.cur_frame = self.cur_frame + 0.1
        self.player_image = self.frames[round(self.cur_frame) % len(self.frames)]
        self.player_image = pygame.transform.scale(self.player_image, (97, 130))
        self.image = pygame.transform.flip(self.player_image, self.left, False)
        if self.damage:
            self.drop()

    def on_the_ground(self):
        # проверка стоит ли наш персонаж на земле
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.top - 23 > self.rect.centery:
                # if not self.bad_moment:
                self.start_camera_dy = camera.dy
                self.rect.bottom = sprite.rect.top + 1
                self.jump = False
                return True
        return False

    def collision_at_the_top(self):
        # столкновение с блоками сверху
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.top <= self.rect.top:
                self.rect.top = sprite.rect.bottom + 1
                if self.jump:
                    self.bad_moment = True
                return True
        return False

    def collision_at_the_right(self):
        # столкновение с блоками справа
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.left <= self.rect.right and not self.rect.bottom == sprite.rect.top + 1:
                if sprite.rect.left < self.rect.left:
                    self.rect.right += 2
                return True
        return False

    def collision_at_the_left(self):
        # столкновение с блоками слева
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.right <= self.rect.right and not self.rect.bottom == sprite.rect.top + 1:
                return True
        return False

    def get_coins(self):
        # собираем монетки
        for sprite in pygame.sprite.spritecollide(self, coin_group, True):
            self.coins += 1

    def death(self):
        end_screen()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill((0, 0, 0))
    pygame.display.set_caption('TheSTHR')
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 0)
    start_screen()

    # прописываем группы спрайтов
    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    surface_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()

    # загружаем картинки объектов
    tile_width = tile_height = 50
    tile_images = {
        'surface': load_image('ground.jpg'),
        'beautiful_surface': load_image('grass.png'),
        'coin': load_image('coins.png'),
        'enemy': load_image('enemy1.png'),
        'enemy_1': load_image('enemy1.png'),
        'table': load_image('table.png')
    }
    heart_image = load_image('heart.png')
    # загружаем уровень
    level_map = load_level('map.map')
    player = generate_level(level_map)

    background = pygame.image.load("data/back123.jpg").convert_alpha()
    background_rect = background.get_rect()
    screen.blit(background, background_rect)

    camera = Camera()
    camera.update(player)
    draw_hearts(player.lives)

    pixel_font = pygame.font.Font('data/pixel1.ttf', 48)
    coins = pixel_font.render('0', 1, (255, 255, 255))
    coins_rect = coins.get_rect(center=(900, 50))

    all_sprites.draw(screen)

    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background, background_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                player.timer += 1
                if player.timer == 3:
                    pygame.time.set_timer(pygame.USEREVENT, 0)
        player.get_keys()
        coins = pixel_font.render(str(player.coins), 1, (255, 255, 255))

        hearts_group.draw(screen)
        all_sprites.draw(screen)
        all_sprites.update()
        screen.blit(coins, coins_rect)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
