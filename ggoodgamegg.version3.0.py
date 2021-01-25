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
            if level[y][x] == '?':
                Tile('enemy', x, y)
            if level[y][x] == ',':
                Tile('coin', x, y)
            if level[y][x] == '@':
                new_player = Player(x, y)
    return new_player, x, y


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


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.speedx = 0
        self.speedy = 0

        self.coins = 0
        self.lives = 3
        self.left = False

        self.frames = []
        self.cut_sheet(load_image('hero1.png'), 3, 1)
        self.cur_frame = 1
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (97, 130))
        self.player_image = pygame.transform.scale(self.image, (97, 130))
        self.rect = self.image.get_rect()

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
            self.speedx = - 5
            self.left = True
        if keystate[pygame.K_RIGHT]:
            self.left = False
            self.speedx = 5
        if keystate[pygame.K_UP] and self.on_the_ground() and not self.collision_at_the_top():
            self.speedy = - 8
            self.rect.y -= 0.4
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
        if not self.on_the_ground():
            self.speedy += 0.4
            self.cur_frame = 0
            self.change_frame()
        else:
            self.speedy = 0

        # проверяем, что наш игрок не ушел за границы карты
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > len(level_map[0]) * tile_width - WIDTH:
            self.rect.right = len(level_map[0]) * tile_width - WIDTH
        # перемещаем игрока
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # перемещаем камеру; проверяем, уходит ли камера за границы карты
        camera.dx -= self.speedx
        camera.dy -= self.speedy
        if camera.dx > 0:
            camera.dx = 0
        if camera.dx < - len(level_map[0]) * tile_width + WIDTH:
            camera.dx = - len(level_map[0]) * tile_width + WIDTH
        if camera.dy < tile_height * 2:
            camera.dy = tile_height * 2
        for sprite in all_sprites:
            if sprite != self:
                camera.apply(sprite)

    def change_frame(self):
        # анимация ходьбы
        self.cur_frame = self.cur_frame + 0.1
        self.player_image = self.frames[round(self.cur_frame) % len(self.frames)]
        self.player_image = pygame.transform.scale(self.player_image, (97, 130))
        self.image = pygame.transform.flip(self.player_image, self.left, False)

    def on_the_ground(self):
        # проверка стоит ли наш персонаж на земле
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.y > self.rect.centery:
                self.rect.bottom = sprite.rect.top + 1
                self.speedy = 0
                return True
        return False

    def collision_at_the_top(self):
        # проверка, нет ли платформы сверху персонажа
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.y < self.rect.centery:
                return True
        return False

    def get_coins(self):
        # собираем монетки
        for sprite in pygame.sprite.spritecollide(self, coin_group, True):
            self.coins += 1


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill((0, 0, 0))
    pygame.display.set_caption('goodgamegg')
    clock = pygame.time.Clock()

    #прописываем группы спрайтов
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
        'enemy': load_image('enemy.png')
    }
    level_map = load_level('map.map')
    player, level_x, level_y = generate_level(level_map)

    background = pygame.image.load("data/back123.png").convert_alpha()
    background_rect = background.get_rect()
    screen.blit(background, background_rect)

    camera = Camera()
    camera.update(player)

    pixel_font = pygame.font.Font('data/pixel1.ttf', 64)
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
        player.get_keys()
        coins = pixel_font.render(str(player.coins), 1, (255, 255, 255))

        all_sprites.draw(screen)
        all_sprites.update()
        screen.blit(coins, coins_rect)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()